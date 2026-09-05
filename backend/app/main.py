from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.profiles.router import router as profiles_router
from app.modules.bands.router import router as bands_router
from app.modules.gigs.router import router as gigs_router
from app.modules.bookings.router import router as bookings_router
from app.modules.chat.router import router as chat_router
from app.modules.matching.router import router as matching_router

app = FastAPI(title="GigBridge API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles_router, prefix="/api/profiles", tags=["profiles"])
app.include_router(bands_router, prefix="/api/bands", tags=["bands"])
app.include_router(gigs_router, prefix="/api/gigs", tags=["gigs"])
app.include_router(bookings_router, prefix="/api/bookings", tags=["bookings"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(matching_router, prefix="/api/matching", tags=["matching"])


@app.get("/health")
def health():
    return {"status": "ok"}
