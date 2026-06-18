from datetime import datetime, timezone

from domain.enums import BookingStatus


class TestBookingsAPI:
    async def test_create_booking_success(self, client):
        payload = {
            "name": "pizza",
            "datetime": datetime.now(timezone.utc).isoformat(),
            "service_type": "cafe",
        }

        resp = await client.post("/bookings/", json=payload)

        assert resp.status_code == 201, f"Expected 201, got {resp.json()}"
        data = resp.json()["data"]
        assert data["name"] == payload["name"]
        assert data["service_type"] == payload["service_type"]
        assert data["status"] == "pending"

    async def test_get_one_booking_success(self, client, pending_booking):
        resp = await client.get(f"/bookings/{pending_booking.id}")

        assert resp.status_code == 200, f"Expected 200, got {resp.json()}"
        data = resp.json()["data"]
        assert data["id"] == str(pending_booking.id)

    async def test_get_one_not_found(self, client, repo_mock):
        repo_mock.get_one.return_value = None
        missing_id = "06a34604-ad70-7293-8000-1f1f876b0000"

        resp = await client.get(f"/bookings/{missing_id}")

        assert resp.status_code == 404, f"Expected 404, got {resp.json()}"

    async def test_get_all_with_pagination(self, client, repo_mock):
        params = {"page": 1, "size": 5}

        resp = await client.get("/bookings/", params=params)

        assert resp.status_code == 200, f"Expected 200, got {resp.json()}"

        body = resp.json()
        meta = body["meta"]

        assert (
            meta["page"] == params["page"]
            and meta["size"] == params["size"]
            and meta["total"] == 1
        )

    async def test_cancel_booking_success(self, client, pending_booking):
        resp = await client.delete(f"/bookings/{pending_booking.id}")

        assert resp.status_code == 204, f"Expected 204, got {resp.text}"

    async def test_cancel_booking_unprocessable(self, client, pending_booking, repo_mock):
        pending_booking.status = BookingStatus.FAILED
        repo_mock.get_one.return_value = pending_booking

        resp = await client.delete(f"/bookings/{pending_booking.id}")

        assert resp.status_code == 422, f"Expected 422, got {resp.json()}"
