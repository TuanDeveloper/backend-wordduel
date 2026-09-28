from sqlalchemy.orm import Session

from app.models.room import Room, RoomPlayer
from app.models.user import User


K_FACTOR = 32


def apply_room_result(db: Session, room: Room, players: list[RoomPlayer] | None = None) -> None:
    """Apply one multiplayer ELO result, protected by the room's row lock."""
    if room.rating_applied:
        return
    players = players or db.query(RoomPlayer).filter(RoomPlayer.room_id == room.id).all()
    if len(players) < 2:
        room.rating_applied = True
        return

    users = (db.query(User)
        .filter(User.id.in_([player.user_id for player in players]))
        .order_by(User.id)
        .with_for_update()
        .all())
    scores = {player.user_id: player.score for player in players}
    highest = max(scores.values())
    winners = {user_id for user_id, score in scores.items() if score == highest}
    old_ratings = {user.id: user.rating for user in users}

    for user in users:
        opponents = [rating for other_id, rating in old_ratings.items() if other_id != user.id]
        average_opponent = sum(opponents) / len(opponents)
        expected = 1 / (1 + 10 ** ((average_opponent - old_ratings[user.id]) / 400))
        if user.id in winners:
            actual = 1.0 if len(winners) == 1 else 0.5
            user.wins += 1 if len(winners) == 1 else 0
        else:
            actual = 0.0
        user.rating = max(0, round(old_ratings[user.id] + K_FACTOR * (actual - expected)))
        user.rated_games += 1

    room.rating_applied = True
