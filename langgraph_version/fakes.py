"""A fake chat model that returns scripted messages, including tool calls (offline tests)."""

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel


class ToolCallingFake(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):
        return self
