import struct
import datetime as dt

from .utils import Snapshot
from .utils import to_stream

UINT64 = 8
UINT32 = 4
CHAR = 1
DOUBLE = 8
FLOAT = 4


class Hello:
    def __init__(self, user_id, username, birth_date, gender):
        self.user_id = user_id
        self.username = username
        self.birth_date = birth_date
        self.gender = gender

    def __repr__(self):
        return f'Hello(user_id={self.user_id}, username={self.username}, ' \
               f'birth_date={self.birth_date}, gender={self.gender})'

    def __str__(self):
        fbirth_date = self.birth_date.strftime('%B %d, %Y')
        if self.gender == 'f':
            fgender = 'female'
        elif self.gender == 'm':
            fgender = 'male'
        else:
            fgender = 'other'
        return f'user {self.user_id}: {self.username}, ' \
               f'born {fbirth_date} ({fgender})'

    def __eq__(self, other):
        if not isinstance(other, Hello):
            return False
        return self.user_id == other.user_id and \
            self.username == other.username and \
            self.birth_date == other.birth_date and \
            self.gender == other.gender

    def serialize(self):
        data = b''
        data += struct.pack('Q', self.user_id)
        data += struct.pack('I', len(self.username))
        data += bytes(self.username, 'utf-8')
        data += struct.pack('I', int(self.birth_date.timestamp()))
        data += struct.pack('c', bytes(self.gender, 'utf-8'))
        return data

    @classmethod
    def deserialize(cls, data):
        stream = to_stream(data)
        user_id, username_len = struct.unpack('QI', stream.read(UINT64+UINT32))
        username = stream.read(username_len).decode('utf-8')
        birth_timestamp, gender = struct.unpack('Ic', stream.read(UINT32+CHAR))
        birth_date = dt.datetime.fromtimestamp(birth_timestamp)
        gender = gender.decode('utf-8')
        # Create hello instance
        return cls(user_id, username, birth_date, gender)


class Config:
    def __init__(self, *fields):
        self.fields = fields

    def __repr__(self):
        return f'Config(fields={self.fields})'

    def __str__(self):
        ffields = ', '.join(self.fields)
        return f'Supported fields: {ffields}'

    def __eq__(self, other):
        if not isinstance(other, Config):
            return False
        return self.fields == other.fields

    def __iter__(self):
        for field in self.fields:
            yield field

    def __contains__(self, field):
        return field in self.fields

    def serialize(self):
        data = b''
        data += struct.pack('I', len(self.fields))
        for field in self.fields:
            data += struct.pack('I', len(field))
            data += bytes(field, 'utf-8')
        return data

    @classmethod
    def deserialize(cls, data):
        stream = to_stream(data)
        fields_num, = struct.unpack('I', stream.read(UINT32))
        # Unpack fields
        fields = []
        for _ in range(fields_num):
            field_len, = struct.unpack('I', stream.read(UINT32))
            fields.append(stream.read(field_len).decode('utf-8'))
        # Create config instance
        return cls(*fields)
