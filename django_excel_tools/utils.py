from .exceptions import SerializerConfigError
try:
    import django

    major, feature, minor, a, b = django.VERSION
    if major >= 2:
        from django.utils.translation import gettext as _
    else:
        from django.utils.translation import ugettext as _
except ImportError:
    raise SerializerConfigError('Django is required. Please make sure you '
                                'have install via pip.')


def error_trans(index, verbose_name, message):
    data = {'index': index, 'verbose_name': verbose_name, 'msg': message}
    return _('[Row %(index)s] %(verbose_name)s %(msg)s') % data
