class BalanceOperation:
    def __init__(self, id: str, receiver_id: str, sender_id: str, amount: int, description: str, createdAt: str, updatedAt: str):
        self.id = id
        self.receiver_id = receiver_id
        self.sender_id = sender_id
        self.amount = amount
        self.description = description
        self.createdAt = createdAt
        self.updatedAt = updatedAt

    def __repr__(self):
        return (f"BalanceOperation(id={self.id}, receiver_id={self.receiver_id}, "
                f"sender_id={self.sender_id}, amount={self.amount}, "
                f"description={self.description}, createdAt={self.createdAt}, "
                f"updatedAt={self.updatedAt})")
