from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ai_core.gemini_generator import (
    GeminiConfigurationError,
    GeminiDocumentGenerator,
    GeminiGenerationError,
)


router = APIRouter()


class DocumentRequest(BaseModel):

    document_type: str = Field(
        ...,
        min_length=2,
        max_length=120
    )

    parties: str = Field(
        ...,
        min_length=2,
        max_length=4000
    )

    terms: str = Field(
        ...,
        min_length=2,
        max_length=10000
    )

    effective_date: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    additional_instructions: str = Field(
        default="",
        max_length=5000
    )


class DocumentResponse(BaseModel):

    document_type: str

    generated_text: str


@router.post(
    "/generate",
    response_model=DocumentResponse
)
def generate_document(
    payload: DocumentRequest
):

    try:

        generator = GeminiDocumentGenerator()

        generated_text = generator.generate_document(

            document_type=payload.document_type,

            parties=payload.parties,

            terms=payload.terms,

            effective_date=payload.effective_date,

            additional_instructions=(
                payload.additional_instructions
            ),
        )

        return DocumentResponse(

            document_type=payload.document_type,

            generated_text=generated_text,
        )

    except GeminiConfigurationError as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc

    except GeminiGenerationError as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc)
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected server error: {exc}"
        ) from exc