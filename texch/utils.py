from texch.exceptions import (
    NotRunYetException, NotTrueLabelsSetException,
    ProxyObjectException
)


def already_run(instance):
    if not instance.is_run:
        raise NotRunYetException("Firstly you need to call .run()")


def true_labels_set(instance):
    if instance.true_labels is None:
        raise NotTrueLabelsSetException("Firstly you need to set true labels")


def not_proxied(instance):
    if instance.is_proxy:
        raise ProxyObjectException(
            'You are calling this method on a '
            'proxied object that behaves like a class.'
            ' Firstly call {0}(...) to create an instance'.format(
                instance.__class__.__name__
            )
        )