# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__author__ = 'www.grillazz.com'

from django.db import models

# Create your models here.


class PdfForms(models.Model):
    formName = models.CharField(max_length=128, verbose_name='Form Name')
    slug = models.SlugField(unique=True)
    pdfFile = models.FileField(upload_to='pdf_forms', verbose_name='Pdf File')

    class Meta:
        verbose_name = "Pdf Form"
        verbose_name_plural = "Pdf Forms"

    def __unicode__(self):
        return '%s' % (self.formName,)

        # def get_absolute_url(self):
        #    return reverse("pdf_url", kwargs={"slug": self.slug})
