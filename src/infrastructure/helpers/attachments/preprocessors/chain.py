import io
import typing

from domain import attachments

FileName: typing.TypeAlias = typing.Text


class AttachmentPreprocessor(typing.Protocol):
    name: typing.Text
    content_type: attachments.AttachmentType

    def __call__(self, file_object: typing.BinaryIO) -> typing.BinaryIO:
        raise NotImplementedError

    def new_filename(self, file_name: FileName) -> FileName:
        raise NotImplementedError


class PreprocessingChain:
    name: typing.Text

    def __init__(
        self,
        chain_name: typing.Text,
        content_type: attachments.AttachmentType,
        preprocessors: typing.List[AttachmentPreprocessor],
    ):
        if any(filter(lambda p: p.content_type != content_type, preprocessors)):  # type: ignore
            raise ValueError(
                f"All preprocessors should have the same "
                f"content type {content_type}: ({', '.join(map(lambda p: p.content_type, preprocessors))})",
            )
        self.name = chain_name
        self.preprocessors = preprocessors
        self.content_type = content_type
        self._context: typing.BinaryIO | None = None
        self._file_name: typing.Text | None = None
        self._iterator: typing.Iterator[AttachmentPreprocessor] | None = None

    def __next__(self) -> typing.Tuple[FileName, typing.BinaryIO]:
        if self._file_name is None or self._context is None or self._iterator is None:
            raise ValueError(
                "Preprocessing chain not initialized. Please call `iterator` method first",
            )

        target_processor = next(self._iterator)
        result = target_processor(file_object=self._context)
        result_data = result.read()
        self._context = io.BytesIO(result_data)
        return target_processor.new_filename(self._file_name), io.BytesIO(result_data)

    def __iter__(self):
        return self

    def iterator(
        self,
        content: typing.BinaryIO,
        file_name: FileName,
    ) -> typing.Self:
        self._context = content
        self._file_name = file_name
        self._iterator = iter(self.preprocessors)
        return iter(self)
