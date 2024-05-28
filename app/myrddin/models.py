from django.db import models
from django.db.models.deletion import PROTECT
from django.db.models.fields import TextField
from django.template.defaultfilters import default
from django.urls import reverse
from enum import unique

import os

class Poem(models.Model):
    merlin_project_number = models.FloatField(blank=False, null=False)
    first_line_modern_orthography = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=False, null=False)
    notes = models.TextField(blank=True, null=True)

class Location(models.Model):
    standard_form = models.CharField(max_length=255)
    english_definition = models.CharField(max_length=255)
    welsh_definition = models.CharField(max_length=255)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)    

class Symbol(models.Model):
    standard_form = models.CharField(max_length=255)
    english_definition = models.CharField(max_length=255, blank=True, null=True)
    welsh_definition = models.CharField(max_length=255,blank=True, null=True)
    see_also = models.CharField(max_length=255, blank=True, null=True)
    
