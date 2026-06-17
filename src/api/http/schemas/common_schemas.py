from pydantic import BaseModel, Field, PositiveInt


class Pagination(BaseModel):
    page: PositiveInt = Field(default=1)
    size: PositiveInt = Field(default=20, le=100)

    @property
    def limit(self) -> int:
        return self.size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size
