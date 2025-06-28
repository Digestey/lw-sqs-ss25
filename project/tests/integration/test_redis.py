import os
import pytest
import json
import time

import app.services.redis_service as redis_service


@pytest.mark.usefixtures("redis_container")
class TestRedisIntegration:

    client_id = "test-client"

    def setup_method(self):
        # Clean up before each test
        redis_service.clear_state(self.client_id)
        redis_service.reset_score(self.client_id)

    def test_set_and_get_state(self):
        sample_data = {"name": "pikachu", "pokemon_id": 25}
        redis_service.set_state(self.client_id, sample_data)
        state = redis_service.get_state(self.client_id)
        assert state == sample_data

    def test_clear_state_removes_data(self):
        redis_service.set_state(self.client_id, {"dummy": "data"})
        redis_service.clear_state(self.client_id)
        assert redis_service.get_state(self.client_id) is None

    def test_increment_and_get_score(self):
        initial_score = redis_service.get_score(self.client_id)
        assert initial_score == 0

        redis_service.increment_score(self.client_id, 10)
        score = redis_service.get_score(self.client_id)
        assert score == 10

        redis_service.increment_score(self.client_id, 5)
        score = redis_service.get_score(self.client_id)
        assert score == 15

    def test_reset_score_deletes_score(self):
        redis_service.increment_score(self.client_id, 20)
        redis_service.reset_score(self.client_id)
        assert redis_service.get_score(self.client_id) == 0

    def test_is_redis_healthy_true(self):
        assert redis_service.is_redis_healthy() is True

    def test_state_expiry(self):
        sample_data = {"name": "eevee"}
        redis_service.set_state(self.client_id, sample_data)
        ttl = redis_service.get_redis_client().ttl(f"quiz:{self.client_id}")
        assert ttl > 0 and ttl <= 1800  # TTL should be set to 1800 seconds or less

    def test_score_expiry(self):
        redis_service.increment_score(self.client_id, 10)
        ttl = redis_service.get_redis_client().ttl(f"quiz:{self.client_id}:score")
        assert ttl > 0 and ttl <= 1800

