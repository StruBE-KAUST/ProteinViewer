from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
import mock
import timeout_decorator

