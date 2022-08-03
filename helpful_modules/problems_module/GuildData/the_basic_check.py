import typing as t

import disnake


class CheckForUserPassage:
    def __init__(
        self,
        blacklisted_users: t.List[int],
        whitelisted_users: t.List[int],
        roles_allowed: t.List[int],
        permissions_needed: t.List[str],
    ):
        self.blacklisted_users = blacklisted_users
        self.whitelisted_users = whitelisted_users
        self.roles_allowed = roles_allowed
        self.permissions_needed = permissions_needed

    def check_for_user_passage(self, member: disnake.Member) -> bool:
        """Return whether the user passes this check. First we check for blacklisted/whitelisted people. Then roles and permissions are checked. If none of those checks succeed, False is returned. Otherwise True is returned"""
        if self._is_undefined:
            return True  # By default, if this check is undefined, it returns True!
        if member.id in self.blacklisted_users:
            return False
        if member.id in self.whitelisted_users:
            return True

        role_ids_of_this_user: set = {
            role.id for role in member.roles
        }  # Create a list containing the ids of the member's roles
        roles_allowed: set = set(self.allowed_roles)
        if (
            role_ids_of_this_user.intersection(roles_allowed) != set()
        ):  # This user has at least 1 of the allowed roles
            return True

        _permissions_needed_dict = dict.fromkeys(self.permission_names_needed, True)
        all_permissions_needed = disnake.Permissions(
            **_permissions_needed_dict
        )  # Create the Permissions instance based on what permissions are required
        if member.guild_permissions.is_superset(all_permissions_needed):
            return True

        return False

    @classmethod
    def from_dict(cls, data: dict) -> "CheckForUserPassage":
        """Convert a dictionary into an instance of CheckForUserPassage"""
        return cls(
            blacklisted_users=data["blacklisted_users"],
            permissions_needed=data["permissions_needed"],
            roles_allowed=data["roles_needed"],
            whitelisted_users=data["whitelisted_users"],
        )

    def to_dict(self):
        """Convert myself to a dictionary"""
        return {
            "blacklisted_users": self.blacklisted_users,
            "whitelisted_users": self.whitelisted_users,
            "roles_allowed": self.roles_allowed,
            "permissions_needed": self.permissions_needed,
        }

    @property
    def _is_undefined(self):
        return (
            self.blacklisted_users == []
            and self.whitelisted_users == []
            and self.roles_allowed == []
            and self.permissions_needed == []
        )

    @classmethod
    def default(cls) -> "CheckForUserPassage":
        return cls(
            blacklisted_users=[],
            whitelisted_users=[],
            roles_allowed=[],
            permissions_needed=[],
        )

    @classmethod
    def default_mod_check(cls) -> "CheckForUserPassage":
        return cls(
            blacklisted_users=[],
            whitelisted_users=[],
            roles_allowed=[],
            permissions_needed=["administrator"],
        )

    def __eq__(self, other):
        if not isinstance(other, CheckForUserPassage):
            return (
                False  # It's not equal to this object because the types are different
            )

        return (
            self.blacklisted_users == other.blacklisted_users
            and other.whitelisted_users == self.whitelisted_users
            and self.permissions_needed == other.permissions_needed
            and self.roles_allowed == other.roles_allowed
        )
    def __repr__(self):
        return f"<CheckForUserPassage roles_needed=[{self.roles_allowed}] blacklisted_users={self.blacklisted_users} whitelisted_users={self.whitelisted_users} permissions_needed = {self.permissions_needed}>"