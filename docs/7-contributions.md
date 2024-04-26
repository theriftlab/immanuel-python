# Contributions

New translations for Immanuel's output are always welcome, although it is currently geared to Western-European languages. If you would like to contribute a translation, follow these steps:

* Fork the repo.
* Create a branch named after the locale, eg. `translations/pr_BR` - locale names for various languages can be found online, for example [here](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oe376/6c085406-a698-4e12-9d4d-c3b0ee3dbc4a), although you should use an underscore rather than a hyphen.
* Create a subdirectory named after your locale code in the existing `/immanuel/locales` directory, and another sub-directory under this called `LC_MESSAGES`.
* Copy `/immanuel/locales/immanuel.pot` into your new `LC_MESSAGES` sub-directory and rename it `immanuel.po`.
* To map noun genders, a file `mappings.py` will need to be created under your new locale directory alongside `LC_MESSAGES`. See existing mapping files for an example of how to assign all of Immanuel's objects a gender for your language.

Your file tree should now look something like this:

```
immanuel/
├- ...
├─ locales/
├- ├- ...
│  ├─ xx_XX/
│  │  ├─ LC_MESSAGES/
│  │  │  ├─ immanuel.po
│  │  ├─ mappings.py
│  ├─ immanuel.pot
```

Now you can begin translating. Within `immanuel.po`, for every English word or sentence in a `msgid` string, if there is a direct translation in your language, enter it in the following empty `msgstr`. For gendered adjectives, you will need to add all gendered variants using `msgctxt` like this:

```
msgctxt "masculine"
msgid "Applicative"
msgstr "Aplicativo"

msgctxt "feminine"
msgid "Applicative"
msgstr "Aplicativa"
```

The masculine and feminine versions of these adjectives (and neuter if applicable) are determined by the relevant noun's gender as specified in your new `mappings.py` file.

Once all translations and gender-mapping is complete, you can either compile your `.po` file to an `.mo` file or simply leave this out and I will compile it.

Time to commit your changes and create a pull request - if everything looks good, I will merge to master & prep a new release!

1. [Overview](1-overview.md)
2. [Installation](2-installation.md)
3. [Examples](3-examples.md)
4. [Returned Data](4-data.md)
5. [Settings](5-settings.md)
6. [Submodules](6-submodules.md)
7. Contributions
