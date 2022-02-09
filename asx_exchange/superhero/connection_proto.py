from abc import abstractmethod
from typing import Protocol

from paper_trader.utils.price import Price

from .types import Holdings, MarketDepth, OrderStatus, Orders, PricingInstruction, SecurityInfo, SecurityPriceTimes, Side

class ConnectionProto(Protocol):
    @property
    def logged_in(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def login(self, username: str | None = None, password: str | None = None):
        raise NotImplementedError()
    
    @abstractmethod
    def logout(self):
        raise NotImplementedError()

    @abstractmethod
    def get_holdings(self) -> Holdings:
        raise NotImplementedError()
    
    @abstractmethod
    def get_security_info(self, security_id: int) -> SecurityInfo:
        raise NotImplementedError()
    
    @abstractmethod
    def get_security_performance(self, security_id: int, date_period: str='1d') -> SecurityPriceTimes:
        raise NotImplementedError()
    
    @abstractmethod
    def get_security_depth(self, security_id: int) -> MarketDepth:
        raise NotImplementedError()
    
    @abstractmethod
    def get_orders(self, status: OrderStatus=OrderStatus.ALL) -> Orders:
        raise NotImplementedError()
    
    @abstractmethod
    def create_order(self, security_id: int, price: Price, volume: int, side: Side, instruction: PricingInstruction) -> int:
        raise NotImplementedError()

    @abstractmethod
    def validate_order(self, security_id: int, price: Price, volume: int, side: Side, instruction: PricingInstruction) -> tuple[bool, dict]:
        raise NotImplementedError()
    
    @abstractmethod
    def cancel_order(self, order_id: int):
        raise NotImplementedError()
        