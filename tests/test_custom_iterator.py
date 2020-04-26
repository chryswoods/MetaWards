
from metawards.iterators import build_custom_iterator, iterate_default, \
                                iterate_weekday


def my_iterator(**kwargs):
    return iterate_weekday(**kwargs)


def iterate_customised(**kwargs):
    return iterate_weekday(**kwargs)


def test_my_custom_iterator():
    print(__name__)

    default_funcs = iterate_default()

    # make sure that build_custom_iterator doesn't change iterate_default
    custom = build_custom_iterator(iterate_default, __name__)

    custom_funcs = custom()

    assert custom_funcs == default_funcs

    # customise from existing function
    custom = build_custom_iterator(my_iterator, __name__)

    custom_funcs = custom()

    assert custom_funcs == default_funcs

    # customise from existing function that is in the metawards.iterators
    # namespace
    custom = build_custom_iterator("iterate_weekday", __name__)

    custom_funcs = custom()

    assert custom_funcs == default_funcs

    # customise from existing function that is already imported
    custom = build_custom_iterator("my_iterator", __name__)

    custom_funcs = custom()

    assert custom_funcs == default_funcs

    # customise from loading the first 'iterate_XXX' function from
    # the specified module (in this case, this script)
    custom = build_custom_iterator("test_custom_iterator", __name__)

    custom_funcs = custom()

    assert custom_funcs == default_funcs

    # customise from loading the specified function in the
    # specified module (in this case, this script)
    custom = build_custom_iterator("test_custom_iterator::my_iterator",
                                   __name__)

    custom_funcs = custom()

    assert custom_funcs == default_funcs


if __name__ == "__main__":
    test_my_custom_iterator()
