"""
NepaliCode Telegram Bot Library
Foundation for Telegram bot development
"""

from typing import Callable, Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class Message:
    """Telegram message object"""
    message_id: int
    text: str
    chat_id: int
    user_id: int
    username: Optional[str] = None
    
    def reply(self, text: str) -> None:
        """Reply to message (placeholder for actual implementation)"""
        print(f"Reply to {self.chat_id}: {text}")


@dataclass
class User:
    """Telegram user object"""
    id: int
    username: Optional[str]
    first_name: str
    last_name: Optional[str] = None


class Bot:
    """Telegram bot foundation"""
    
    def __init__(self, token: str):
        self.token = token
        self.commands: Dict[str, Callable] = {}
        self.handlers: List[Callable] = []
    
    def command(self, command: str, handler: Callable) -> None:
        """Register command handler"""
        self.commands[command] = handler
    
    def message_handler(self, handler: Callable) -> None:
        """Register message handler"""
        self.handlers.append(handler)
    
    def send_message(self, chat_id: int, text: str) -> None:
        """Send message (placeholder for actual implementation)"""
        print(f"Sending to {chat_id}: {text}")
    
    def run(self) -> None:
        """Start bot (placeholder for actual implementation)"""
        print("Bot started (placeholder - needs actual Telegram API integration)")
        print(f"Registered commands: {list(self.commands.keys())}")


class InlineKeyboard:
    """Inline keyboard for messages"""
    
    def __init__(self):
        self.buttons: List[List[Dict[str, Any]]] = []
    
    def add_button(self, text: str, callback_data: str) -> None:
        """Add button to keyboard"""
        if not self.buttons:
            self.buttons.append([])
        self.buttons[-1].append({
            "text": text,
            "callback_data": callback_data
        })
    
    def add_row(self) -> None:
        """Add new row"""
        self.buttons.append([])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API"""
        return {"inline_keyboard": self.buttons}


class ReplyKeyboard:
    """Reply keyboard for messages"""
    
    def __init__(self, resize_keyboard: bool = True):
        self.buttons: List[List[str]] = []
        self.resize_keyboard = resize_keyboard
    
    def add_button(self, text: str) -> None:
        """Add button to keyboard"""
        if not self.buttons:
            self.buttons.append([])
        self.buttons[-1].append(text)
    
    def add_row(self) -> None:
        """Add new row"""
        self.buttons.append([])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API"""
        return {
            "keyboard": self.buttons,
            "resize_keyboard": self.resize_keyboard
        }


# For interpreter context
_module_dict = {
    'Bot': Bot,
    'Message': Message,
    'User': User,
    'InlineKeyboard': InlineKeyboard,
    'ReplyKeyboard': ReplyKeyboard,
}