import contextlib
from peewee import *


class FileManager:
    def __init__(self, db: SqliteDatabase):
        class File(Model):
            file_name = CharField()
            mode = CharField()
            description = CharField(null=True)
            content = TextField(null=True)
            unique_id = CharField(primary_key=True, unique=True)

            class Meta:
                database = db

        self.model = File
        db.connect(reuse_if_open=True)
        db.create_tables([File], safe=True)

    def create_file(
        self,
        file_name: str,
        description: str,
        content: str,
        mode: str
    ):
        unique_id = f"{mode}_{file_name}"
        with contextlib.suppress(Exception):
            file = self.model(
                file_name=file_name,
                description=description,
                content=content,
                unique_id=unique_id,
                mode=mode
            )
            file.save(force_insert=True)

    def read_file(self, mode: str, file_name: str):
        unique_id = f"{mode}_{file_name}"
        print(unique_id)
        try:
            return self.model.get(self.model.unique_id == unique_id)
        except DoesNotExist:
            return None

    def update_file(self, mode: str, file_name: str, attributes: dict):
        unique_id = f"{mode}_{file_name}"
        file = self.model.get(self.model.unique_id == unique_id)
        for attr, value in attributes.items():
            setattr(file, attr, value)
        file.save()

    def delete_file(self, mode: str, file_name: str):
        unique_id = f"{mode}_{file_name}"
        file = self.model.get(self.model.unique_id == unique_id)
        file.delete_instance()

    def select_files_with_mode(self, mode: str):
        return list(self.model.select().where(self.model.mode == mode))

    def get_all_files(self) -> list:
        return list(self.model.select())

    def get_cls(self):
        return self.model
    
class ChatManager:
    def __init__(self, db: SqliteDatabase) -> None:
        
        class ChatMessage(Model):
            ai_message = TextField()
            human_message = TextField()
            sequence_number = IntegerField()
            namespace = CharField()
            file_name = CharField()
            title = CharField()

            class Meta:
                database = db
                
        self.model = ChatMessage
        db.connect(reuse_if_open=True)
        db.create_tables([ChatMessage], safe=True)
        
    def add_message(self, namespace: str, ai_message: str, human_message: str, file_name: str, title: str) -> None:
        last_message = self.model.select().where(self.model.namespace == namespace).order_by(
            self.model.sequence_number.desc()).first()

        if last_message is None:
            sequence_number = 0
        else:
            sequence_number = last_message.sequence_number + 1

        self.model.create(namespace=namespace, ai_message=ai_message, human_message=human_message,
                            sequence_number=sequence_number, file_name=file_name, title=title)

    def retrieve_all_messages(self, namespace: str):
        query = self.model.select().where(self.model.namespace == namespace).order_by(self.model.sequence_number)
        return [(row.human_message, row.ai_message) for row in query]


    def get_all_conversations_for_file(self,filename):
        return [
            record
            for record in (
                list(
                    self.model.select().where(
                        self.model.file_name == filename
                    )
                )
            )
        ]
        

if __name__ == "__main__":
    manager = ChatManager(SqliteDatabase("database.db"))
    print(manager.get_all_conversations_for_file("paper_2_18beb447_pdf"))
