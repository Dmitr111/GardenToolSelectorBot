from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.review import Review

class ReviewRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Review:
        return await self.session.scalar(select(Review).where(Review.id == id))
    
    async def get_by_user_and_tool(self, user_id: int, tool_id: int) -> Review:
        return await self.session.scalar(
            select(Review).where(
                Review.user_id == user_id,
                Review.tool_id == tool_id
            ))

    async def get_all_for_tool(self, tool_id: int, exclude_user_id: int = None) -> list[Review]:
        query = select(Review).where(Review.tool_id == tool_id)
        
        if exclude_user_id:
            query = query.where(Review.user_id != exclude_user_id)
            
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_or_update(self, user_id: int, tool_id: int, text: str, rating: int) -> Review:
        review = await self.get_by_user_and_tool(user_id, tool_id)
        
        if not review:
            review = Review(
                user_id=user_id,
                tool_id=tool_id,
                text=text,
                rating=rating
            )
            self.session.add(review)
        else:
            review.text = text
            review.rating = rating
            
        await self.session.commit()
        return review

    async def delete(self, user_id: int, tool_id: int) -> bool:
        review = await self.get_by_user_and_tool(user_id, tool_id)
        if not review:
            return False
            
        await self.session.delete(review)
        await self.session.commit()
        return True
    
    async def exists(self, user_id: int, tool_id: int) -> bool:
        review = await self.get_by_user_and_tool(user_id, tool_id)
        return review is not None