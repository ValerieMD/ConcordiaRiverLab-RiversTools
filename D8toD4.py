# coding: latin-1

#####################################################
# Gu�nol� Chon�
# Concordia University
# Geography, Planning and Environment Department
# guenole.chone@concordia.ca
#####################################################

# Versions
# v1.0 - Mars 2017 - Cr�ation
# v1.1 - Avril 2020 - S�paration de l'interface et du m�tier
# v1.1 - Mai 2020 - Ajout du param�tre Workspace. D�bug confluence et double lignes.


from RasterIO import *


def execute_D8toD4(r_flowdir, r_dem, str_frompoint, str_result, messages, language = "FR"):
    """The source code of the tool."""


    # Chargement des fichiers
    flowdir = RasterIO(r_flowdir)
    dem = RasterIO(r_dem)
    try:
        dem.checkMatch(flowdir)
    except Exception as e:
        messages.addErrorMessage(e.message)

    Result = RasterIO(r_flowdir, str_result, int, -255)

    # Traitement effectu� pour chaque point de d�part
    frompointcursor = arcpy.da.SearchCursor(str_frompoint, "SHAPE@")
    for frompoint in frompointcursor:

        # On prend l'objet g�om�trique (le point) associ� � la ligne dans la table
        frompointshape = frompoint[0].firstPoint

        # Conversion des coordonn�es
        currentcol = flowdir.XtoCol(frompointshape.X)
        currentrow = flowdir.YtoRow(frompointshape.Y)


        intheraster = True
        # Tests de s�curit� pour s'assurer que le point de d�part est � l'int�rieurs des rasters
        if currentcol<0 or currentcol>=flowdir.raster.width or currentrow<0 or currentrow>= flowdir.raster.height:
            intheraster = False
        elif (flowdir.getValue(currentrow, currentcol) <> 1 and flowdir.getValue(currentrow, currentcol) <> 2 and
                            flowdir.getValue(currentrow, currentcol) <> 4 and flowdir.getValue(currentrow, currentcol) <> 8 and
                            flowdir.getValue(currentrow, currentcol) <> 16 and flowdir.getValue(currentrow, currentcol) <> 32 and flowdir.getValue(currentrow, currentcol) <> 64 and flowdir.getValue(currentrow, currentcol) <> 128):
            intheraster = False

        # Traitement effectu� sur chaque cellule le long de l'�coulement
        lastdir = 0
        while (intheraster):

            # On regarde la valeur du "flow direction"
            direction = flowdir.getValue(currentrow, currentcol)

            # Si cette valeur est 1, 4, 16 ou 64, on se d�place sur des cases adjacentes. On garde la valeur.
            # Si cette valeur est 2, 8, 32 ou 128, on se d�place en diagonale. Un traitement est n�cesaire.

            if (direction == 1):
                Result.setValue(currentrow, currentcol, direction)
                currentcol = currentcol + 1
                lastdir = 1

            if (direction == 2):
                if lastdir == 16:
                    #shortcut
                    Result.setValue(currentrow, currentcol + 1, 4)
                    lastdir = 4
                elif lastdir == 64:
                    Result.setValue(currentrow + 1, currentcol, 1)
                    lastdir = 1
                else:
                    # on regarde, parmi les deux cellules adjacentes pouvant remplacer le d�placement en diagonale, quelle est celle d'�l�vation la plus basse, et on passe par celle-ci
                    # exemple : direction = 2 -> on se d�place en diagonale, en bas � droite
                    # on peut donc remplacer ce d�placement par aller � droite (flow direction = 1) puis aller en bas (flow direction = 4) ou bien aller en bas puis aller � droite
                    if dem.getValue(currentrow, currentcol + 1) < dem.getValue(currentrow + 1, currentcol):
                        # La cellule � droite � une �l�vation plus basse que la cellule en bas, on choisie donc d'aller � droite puis ensuite en bas
                        # On modifie donc le flow direction pour aller � droite
                        Result.setValue(currentrow, currentcol, 1)
                        # Puis on modifie le flow direction du la cellule � droite pour aller en bas
                        if (Result.getValue(currentrow, currentcol+1) <> -255):
                            # Atteinte d'un confluent
                            intheraster = False
                        else:
                            Result.setValue(currentrow, currentcol+1, 4)
                            lastdir = 4

                    else:
                        Result.setValue(currentrow, currentcol, 4)
                        if (Result.getValue(currentrow+1, currentcol) <> -255):
                            # Atteinte d'un confluent
                            intheraster = False
                        else:
                            Result.setValue(currentrow+1, currentcol, 1)
                            lastdir = 1
                currentcol = currentcol + 1
                currentrow = currentrow + 1

            if (direction == 4):
                Result.setValue(currentrow, currentcol, direction)
                currentrow = currentrow + 1
                lastdir = 4

            if (direction == 8):
                if lastdir == 1:
                    #shortcut
                    Result.setValue(currentrow, currentcol - 1, 4)
                    lastdir = 4
                elif lastdir == 64:
                    Result.setValue(currentrow + 1, currentcol, 16)
                    lastdir = 16
                else:
                    if dem.getValue(currentrow+1, currentcol) < dem.getValue(currentrow, currentcol-1):
                        Result.setValue(currentrow, currentcol, 4)
                        if (Result.getValue(currentrow+1, currentcol) <> -255):
                            # Atteinte d'un confluent
                            intheraster = False
                        else:
                            Result.setValue(currentrow+1, currentcol, 16)
                            lastdir = 16
                    else:
                        Result.setValue(currentrow, currentcol, 16)
                        if (Result.getValue(currentrow, currentcol-1) <> -255):
                            # Atteinte d'un confluent
                            intheraster = False
                        else:
                            Result.setValue(currentrow, currentcol-1, 4)
                            lastdir = 4
                currentcol = currentcol - 1
                currentrow = currentrow + 1

            if (direction == 16):
                Result.setValue(currentrow, currentcol, direction)
                currentcol = currentcol - 1
                lastdir = 16

            if (direction == 32):
                if lastdir == 1:
                    #shortcut
                    Result.setValue(currentrow, currentcol - 1, 64)
                    lastdir = 64
                elif lastdir == 4:
                    Result.setValue(currentrow - 1, currentcol, 16)
                    lastdir = 16
                else:
                    if dem.getValue(currentrow-1, currentcol) < dem.getValue(currentrow, currentcol-1):
                        Result.setValue(currentrow, currentcol, 64)
                        if (Result.getValue(currentrow-1, currentcol) <> -255):
                            # Atteinte d'un confluent
                            intheraster = False
                        else:
                            Result.setValue(currentrow-1, currentcol, 16)
                            lastdir = 16
                    else:
                        Result.setValue(currentrow, currentcol, 16)
                        if (Result.getValue(currentrow, currentcol-1) <> -255):
                            # Atteinte d'un confluent
                            intheraster = False
                        else:
                            Result.setValue(currentrow, currentcol-1, 64)
                            lastdir = 64
                currentcol = currentcol - 1
                currentrow = currentrow - 1

            if (direction == 64):
                Result.setValue(currentrow, currentcol, direction)
                currentrow = currentrow - 1
                lastdir = 64

            if (direction == 128):
                if lastdir == 16:
                    #shortcut
                    Result.setValue(currentrow, currentcol + 1, 64)
                    lastdir = 64
                elif lastdir == 4:
                    Result.setValue(currentrow - 1, currentcol, 1)
                    lastdir = 1
                else:
                    if dem.getValue(currentrow-1, currentcol) < dem.getValue(currentrow, currentcol+1):
                        Result.setValue(currentrow, currentcol, 64)
                        if (Result.getValue(currentrow-1, currentcol) <> -255):
                            # Atteinte d'un confluent
                            intheraster = False
                        else:
                            Result.setValue(currentrow-1, currentcol, 1)
                            lastdir = 1
                    else:
                        Result.setValue(currentrow, currentcol, 1)
                        if (Result.getValue(currentrow, currentcol+1) <> -255):
                            # Atteinte d'un confluent
                            intheraster = False
                        else:
                            Result.setValue(currentrow, currentcol+1, 64)
                            lastdir = 64
                currentcol = currentcol + 1
                currentrow = currentrow - 1


            if currentcol < 0 or currentcol >= flowdir.raster.width or currentrow < 0 or currentrow >= flowdir.raster.height:
                intheraster = False
            elif (flowdir.getValue(currentrow, currentcol) <> 1 and flowdir.getValue(currentrow, currentcol) <> 2 and
                            flowdir.getValue(currentrow, currentcol) <> 4 and flowdir.getValue(currentrow, currentcol) <> 8 and
                            flowdir.getValue(currentrow, currentcol) <> 16 and flowdir.getValue(currentrow, currentcol) <> 32 and flowdir.getValue(currentrow, currentcol) <> 64 and flowdir.getValue(currentrow, currentcol) <> 128):
                intheraster = False

            if intheraster:
                if (Result.getValue(currentrow, currentcol) <> -255):
                    # Atteinte d'un confluent
                    intheraster = False




    Result.save()


    return