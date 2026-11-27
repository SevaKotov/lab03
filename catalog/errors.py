class CatalogError(Exception):
    pass

class InvalidEntity(CatalogError):
    pass

class DoubleID(CatalogError):
    pass

class UndefinedObject(CatalogError):
    pass

class UndefinedFormatVersion(CatalogError):
    pass

class CorruptedFile(CatalogError):
    pass

class Invalid_Path(CatalogError):
    pass