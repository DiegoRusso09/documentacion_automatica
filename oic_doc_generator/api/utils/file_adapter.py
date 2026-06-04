from io import BytesIO

def to_stream(
    upload_file
):

    content = upload_file.file.read()

    stream = BytesIO(content)

    stream.name = (
        upload_file.filename
    )

    return stream