import cqrs

from service import unit_of_work
from service.requests.chats import get_chats


class GetChatsHandler(cqrs.RequestHandler[get_chats.GetChats, get_chats.Chats]):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self):
        return list(self.uow.get_events())

    async def handle(self, request: get_chats.GetChats) -> get_chats.Chats:
        async with self.uow:
            chats = await self.uow.chat_repository.get_all(
                request.participant,
                with_participants=request.with_participant_ids,
                strict_participants_search=request.strict_participants_search,
            )
            if request.chat_ids is not None:
                chats = list(
                    filter(
                        lambda chat: chat.chat_id in request.chat_ids or [],  # pyright: ignore[reportOperatorIssue]
                        chats,
                    ),
                )
            last_read_messages = await self.uow.read_message_repository.last_read_many(
                account_id=request.participant,
                chat_ids=[chat.chat_id for chat in chats],
            )
            not_read_messages_count = await self.uow.chat_repository.count_after_many(
                *[
                    (chat_id, last_message_id)
                    for chat_id, last_message_id in zip(
                        [chat.chat_id for chat in chats],
                        [last_msg.message.message_id if last_msg else None for last_msg in last_read_messages],
                    )
                ],
            )

            chats_info = []

            for chat, last_read, not_read_count in zip(
                chats,
                last_read_messages,
                not_read_messages_count,
            ):
                participant = chat.is_participant(request.participant)
                if participant is None:
                    continue
                chat_info = get_chats.ChatInfo(
                    chat_id=chat.chat_id,
                    name=chat.name,
                    avatar=chat.avatar,
                    participants_count=chat.participants_count,
                    tags=[tag.tag for tag in participant.tags],
                    not_read_messages_count=not_read_count,
                    last_activity_timestamp=chat.last_activity_timestamp,
                    last_message_id=chat.last_message_id,
                    last_read_message_id=last_read.message.message_id if last_read else None,
                )
                chats_info.append(chat_info)

            sorted_chats = sorted(
                chats_info,
                key=lambda x: x.last_activity_timestamp,
                reverse=True,
            )
            return get_chats.Chats(chats=list(sorted_chats))
