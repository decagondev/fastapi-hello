"""A small, deliberately over-engineered FastAPI service.

Layering (dependencies point inwards only)::

    api  ->  services  ->  domain  <-  infrastructure
                 ^                          |
                 +------ core.container ----+
"""

__all__ = ["__version__"]
__version__ = "0.1.0"
