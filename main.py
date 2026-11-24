from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.message_components import Plain
from astrbot.api.star import Context, Star


class KeywordFilter(Star):
    """机器人发出的消息里，命中的关键词会被直接删掉。"""

    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

    @filter.on_decorating_result(priority=100)
    async def strip_keywords(self, event: AstrMessageEvent):
        result = event.get_result()
        if not result or not result.chain:
            return

        # 长的关键词先删，避免 "今天" 和 "今天天气" 这类重叠时删不干净
        words = sorted(
            (w for w in self.config.get("keywords", []) if isinstance(w, str) and w),
            key=len,
            reverse=True,
        )
        if not words:
            return

        new_chain = []
        for comp in result.chain:
            if isinstance(comp, Plain):
                text = comp.text
                for w in words:
                    text = text.replace(w, "")
                if text != comp.text:
                    logger.debug("[keyword_filter] 已过滤关键词")
                    if not text.strip():
                        continue  # 整段被删空了就不发这一段
                    comp.text = text
            new_chain.append(comp)
        result.chain = new_chain
