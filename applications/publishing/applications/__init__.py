from applications.publishing.applications.post import PostApplication

__all__ = [
    "Registry",
]


class Registry:
    PostApplication = PostApplication()
