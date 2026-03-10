from __future__ import annotations


APP_LABEL_TO_DB = {
    "orchestration_service": "default",
    "vehicle_service": "vehicle",
    "zone_service": "zone",
    "parking_command_service": "parking_command",
    "parking_query_service": "parking_query",
}


class ServiceDatabaseRouter:
    def db_for_read(self, model, **hints):
        return APP_LABEL_TO_DB.get(model._meta.app_label)

    def db_for_write(self, model, **hints):
        return APP_LABEL_TO_DB.get(model._meta.app_label)

    def allow_relation(self, obj1, obj2, **hints):
        db1 = APP_LABEL_TO_DB.get(obj1._meta.app_label, "default")
        db2 = APP_LABEL_TO_DB.get(obj2._meta.app_label, "default")
        if db1 == db2:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        target_db = APP_LABEL_TO_DB.get(app_label, "default")
        return db == target_db
