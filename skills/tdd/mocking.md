# When to Mock

Mock at **system boundaries** only:

- External APIs (payment, email, etc.)
- Databases (sometimes - prefer test DB)
- Time/randomness
- File system (sometimes)

Don't mock:

- Your own classes/modules
- Internal collaborators
- Anything you control

## Designing for Mockability

At system boundaries, design interfaces that are easy to mock:

**1. Use dependency injection**

Pass external dependencies in rather than creating them internally:

```python
# Easy to mock
def process_payment(order, payment_client):
    return payment_client.charge(order.total)

# Hard to mock
def process_payment(order):
    client = StripeClient(os.environ["STRIPE_KEY"])
    return client.charge(order.total)
```

Use `mocker.patch` (pytest-mock) at system boundaries in tests; `unittest.mock.patch` via decorator works too for standalone files:

```python
def test_process_payment_charges_correct_amount(mocker):
    mock_client = mocker.patch("myapp.payments.StripeClient")
    mock_client.return_value.charge.return_value = {"status": "ok"}
    result = process_payment(order, mock_client.return_value)
    assert result["status"] == "ok"
```

**2. Prefer SDK-style interfaces over generic fetchers**

Create specific functions for each external operation instead of one generic function with conditional logic:

```python
# GOOD: Each function is independently mockable
class ApiClient:
    def get_user(self, user_id): ...
    def get_orders(self, user_id): ...
    def create_order(self, data): ...

# BAD: Mocking requires conditional logic inside the mock
class ApiClient:
    def fetch(self, endpoint, method="GET", body=None): ...
```

The SDK approach means:
- Each mock returns one specific shape
- No conditional logic in test setup
- Easier to see which endpoints a test exercises
