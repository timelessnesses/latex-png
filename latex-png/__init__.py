import io
import traceback
import typing

import fastapi
import matplotlib
import matplotlib.pyplot

app = fastapi.FastAPI(title="Latex to PNG", docs_url="/")

matplotlib.pyplot.rcParams["text.usetex"] = True


@app.get(
    "/render",
    summary="Render LATEX string to a picture",
    responses={
        200: {
            "description": "Successfully rendering your LATEX string",
            "content": {"image/png": {}, "image/jpeg": {}},
        },
        500: {
            "description": "Failed to render your LATEX string",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "text": "Error messages from matplotlib.pyplot",
                    }
                }
            },
        },
    },
)
async def render(
    latex: str,
    font: typing.Literal["dejavusans", "dejavuserif", "cm", "stix", "stixsans"] = "cm",
    size: int = 16,
    dpi: float = 100.0,
    pic_format: typing.Literal["png", "jpeg"] = "png",
    img_size_x: float | None = None,
    img_size_y: float | None = None,
) -> typing.Any:
    if not "$" in latex:
        return fastapi.responses.JSONResponse(
            {"status": "failed", "reason": "need $ to wrap expression as latex"}, 400
        )

    matplotlib.pyplot.rcParams["mathtext.fontset"] = font
    fig = matplotlib.pyplot.figure(
        dpi=dpi, figsize=(img_size_x, img_size_y) if img_size_y and img_size_x else None
    )
    fig.text(
        x=0.5,
        y=0.5,
        s=latex,
        horizontalalignment="center",
        verticalalignment="center",
        fontsize=size,
    )
    b = io.BytesIO()
    try:
        fig.savefig(b, format=pic_format)
        b.seek(0)
        return fastapi.responses.StreamingResponse(b, media_type=f"image/{pic_format}")
    except RuntimeError as e:
        traceback.print_exception(e)
        return fastapi.responses.JSONResponse(
            {"status": "error", "text": e.args[0]}, 500
        )
