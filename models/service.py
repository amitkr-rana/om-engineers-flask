from datetime import datetime
from typing import Dict, List, Optional

class Service:
    _services: Dict[int, 'Service'] = {}
    _next_id = 1

    def __init__(self, name: str, description: str, category: str, duration: str,
                 price_range: str, icon: str = "🔧", service_id: Optional[int] = None):
        self.id = service_id if service_id is not None else Service._next_id
        Service._next_id = max(Service._next_id, self.id) + 1

        self.name = name
        self.description = description
        self.category = category
        self.duration = duration
        self.price_range = price_range
        self.icon = icon
        self.is_active = True
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

        # Store in memory
        Service._services[self.id] = self

    def to_dict(self) -> Dict:
        """Convert service to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'duration': self.duration,
            'price_range': self.price_range,
            'icon': self.icon,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def update(self, **kwargs) -> None:
        """Update service attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.now()

    def deactivate(self) -> None:
        """Deactivate the service"""
        self.is_active = False
        self.updated_at = datetime.now()

    def activate(self) -> None:
        """Activate the service"""
        self.is_active = True
        self.updated_at = datetime.now()

    @classmethod
    def create(cls, name: str, description: str, category: str, duration: str,
               price_range: str, icon: str = "🔧") -> 'Service':
        """Create a new service"""
        return cls(name=name, description=description, category=category,
                   duration=duration, price_range=price_range, icon=icon)

    @classmethod
    def get_by_id(cls, service_id: int) -> Optional['Service']:
        """Get service by ID"""
        return cls._services.get(service_id)

    @classmethod
    def get_all(cls, active_only: bool = True) -> List['Service']:
        """Get all services"""
        services = list(cls._services.values())
        if active_only:
            services = [s for s in services if s.is_active]
        return services

    @classmethod
    def get_by_category(cls, category: str, active_only: bool = True) -> List['Service']:
        """Get services by category"""
        services = [s for s in cls._services.values() if s.category.lower() == category.lower()]
        if active_only:
            services = [s for s in services if s.is_active]
        return services

    @classmethod
    def search(cls, query: str, active_only: bool = True) -> List['Service']:
        """Search services by name, description, or category"""
        query = query.lower().strip()
        results = []

        for service in cls._services.values():
            if active_only and not service.is_active:
                continue

            if (query in service.name.lower() or
                query in service.description.lower() or
                query in service.category.lower()):
                results.append(service)

        return results

    @classmethod
    def get_categories(cls, active_only: bool = True) -> List[str]:
        """Get all unique service categories"""
        categories = set()
        for service in cls._services.values():
            if active_only and not service.is_active:
                continue
            categories.add(service.category)
        return sorted(list(categories))

    @classmethod
    def delete(cls, service_id: int) -> bool:
        """Delete service by ID"""
        if service_id in cls._services:
            del cls._services[service_id]
            return True
        return False

    @classmethod
    def initialize_default_services(cls):
        """Initialize default services from config"""
        # Only initialize if no services exist
        if cls._services:
            return

        default_services = [
            {
                'name': 'Electrical Repair',
                'description': 'Complete electrical solutions for your home including wiring, outlets, and fixtures',
                'category': 'Electrical',
                'duration': '2-4 hours',
                'price_range': '₹500 - ₹2000',
                'icon': '⚡'
            },
            {
                'name': 'Plumbing Services',
                'description': 'Professional plumbing repairs and installations for all your water-related needs',
                'category': 'Plumbing',
                'duration': '1-3 hours',
                'price_range': '₹300 - ₹1500',
                'icon': '🔧'
            },
            {
                'name': 'AC Repair & Service',
                'description': 'Air conditioning repair, maintenance, and installation services',
                'category': 'HVAC',
                'duration': '1-2 hours',
                'price_range': '₹800 - ₹3000',
                'icon': '❄️'
            },
            {
                'name': 'Home Appliance Repair',
                'description': 'Repair services for washing machines, refrigerators, microwaves, and more',
                'category': 'Appliances',
                'duration': '2-3 hours',
                'price_range': '₹600 - ₹2500',
                'icon': '🏠'
            },
            {
                'name': 'Carpentry Services',
                'description': 'Furniture repair, custom woodwork, and carpentry solutions',
                'category': 'Carpentry',
                'duration': '3-6 hours',
                'price_range': '₹1000 - ₹5000',
                'icon': '🔨'
            },
            {
                'name': 'Painting Services',
                'description': 'Interior and exterior painting services for homes and offices',
                'category': 'Painting',
                'duration': '4-8 hours',
                'price_range': '₹1500 - ₹8000',
                'icon': '🎨'
            },
            {
                'name': 'Cleaning Services',
                'description': 'Deep cleaning, regular maintenance, and specialized cleaning services',
                'category': 'Cleaning',
                'duration': '2-4 hours',
                'price_range': '₹800 - ₹3000',
                'icon': '🧹'
            },
            {
                'name': 'Pest Control',
                'description': 'Safe and effective pest control solutions for your home',
                'category': 'Pest Control',
                'duration': '1-2 hours',
                'price_range': '₹1000 - ₹4000',
                'icon': '🐛'
            }
        ]

        for service_data in default_services:
            cls.create(**service_data)

    def __str__(self) -> str:
        return f"Service(id={self.id}, name='{self.name}', category='{self.category}')"

    def __repr__(self) -> str:
        return self.__str__()