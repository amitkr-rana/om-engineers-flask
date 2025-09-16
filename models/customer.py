from datetime import datetime
from typing import Dict, List, Optional

class Customer:
    _customers: Dict[int, 'Customer'] = {}
    _next_id = 1

    def __init__(self, name: str, email: str, phone: str, address: str = "", customer_id: Optional[int] = None):
        self.id = customer_id if customer_id is not None else Customer._next_id
        Customer._next_id = max(Customer._next_id, self.id) + 1

        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

        # Store in memory
        Customer._customers[self.id] = self

    def to_dict(self) -> Dict:
        """Convert customer to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def update(self, **kwargs) -> None:
        """Update customer attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.now()

    @classmethod
    def create(cls, name: str, email: str, phone: str, address: str = "") -> 'Customer':
        """Create a new customer"""
        return cls(name=name, email=email, phone=phone, address=address)

    @classmethod
    def get_by_id(cls, customer_id: int) -> Optional['Customer']:
        """Get customer by ID"""
        return cls._customers.get(customer_id)

    @classmethod
    def get_by_email(cls, email: str) -> Optional['Customer']:
        """Get customer by email"""
        for customer in cls._customers.values():
            if customer.email.lower() == email.lower():
                return customer
        return None

    @classmethod
    def get_by_phone(cls, phone: str) -> Optional['Customer']:
        """Get customer by phone number"""
        # Clean phone number for comparison
        clean_phone = ''.join(filter(str.isdigit, phone))
        for customer in cls._customers.values():
            customer_clean_phone = ''.join(filter(str.isdigit, customer.phone))
            if customer_clean_phone == clean_phone:
                return customer
        return None

    @classmethod
    def get_all(cls) -> List['Customer']:
        """Get all customers"""
        return list(cls._customers.values())

    @classmethod
    def search(cls, query: str) -> List['Customer']:
        """Search customers by name, email, or phone"""
        query = query.lower().strip()
        results = []

        for customer in cls._customers.values():
            if (query in customer.name.lower() or
                query in customer.email.lower() or
                query in customer.phone):
                results.append(customer)

        return results

    @classmethod
    def delete(cls, customer_id: int) -> bool:
        """Delete customer by ID"""
        if customer_id in cls._customers:
            del cls._customers[customer_id]
            return True
        return False

    @classmethod
    def exists(cls, email: str = None, phone: str = None) -> bool:
        """Check if customer exists by email or phone"""
        if email and cls.get_by_email(email):
            return True
        if phone and cls.get_by_phone(phone):
            return True
        return False

    @classmethod
    def get_or_create(cls, name: str, email: str, phone: str, address: str = "") -> tuple['Customer', bool]:
        """Get existing customer or create new one. Returns (customer, created)"""
        # Try to find existing customer by email or phone
        existing = cls.get_by_email(email) or cls.get_by_phone(phone)

        if existing:
            # Update existing customer info if provided
            updates = {}
            if existing.name != name:
                updates['name'] = name
            if existing.address != address and address:
                updates['address'] = address
            if existing.email != email:
                updates['email'] = email
            if existing.phone != phone:
                updates['phone'] = phone

            if updates:
                existing.update(**updates)

            return existing, False
        else:
            # Create new customer
            new_customer = cls.create(name=name, email=email, phone=phone, address=address)
            return new_customer, True

    def __str__(self) -> str:
        return f"Customer(id={self.id}, name='{self.name}', email='{self.email}')"

    def __repr__(self) -> str:
        return self.__str__()