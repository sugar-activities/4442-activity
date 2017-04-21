#! /usr/bin/env python
# Conozco
# Copyright (C) 2010 Gabriel Eirea
#
# Primer version de Conozco Elementos Quimicos yyaaeell@hotmail.com, rosanor43@hotmail.com
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact information:
# Christofer Roibal yyaaeell@hotmail.com
# Rosamel Norma Ramirez rosanor43@hotmail.com
# Gabriel Eirea geirea@gmail.com
# Ceibal Jam http://ceibaljam.org

import sys
import random
import os
import pygame
import olpcgames
import gtk

# constantes
XMAPAMAX = 810
DXPANEL = 390
XCENTROPANEL = 995
YGLOBITO = 100
DXBICHO = 236
DYBICHO = 357
XNAVE = 836
YNAVE = 510
DXNAVE = 156
DYNAVE = 219
XBICHO = 1200-DXBICHO
YBICHO = 900-DYBICHO
CAMINORECURSOS = "recursos"
CAMINOLAMINA = "lamina"
CAMINOCOMUN = "comun"
CAMINOFUENTES = "fuentes"
ARCHIVOINFO = "info.txt"
CAMINODATOS = "datos"
ARCHIVONIVELES = "niveles.txt"
ARCHIVOZONAS = "zonas.txt"
ARCHIVOCREDITOS = "creditos.txt"
ARCHIVOPRES = "presentacion.txt"
ARCHIVONOMBRE = "nombre.txt"
CAMINOIMAGENES = "imagenes"
CAMINOSONIDOS = "sonidos"
COLORNOMBREDEPTO = (200,60,60)
COLORPREGUNTAS = (80,80,155)
COLORPANEL = (221,221,221)
TOTALAVANCE = 7
EVENTORESPUESTA = pygame.USEREVENT+1
TIEMPORESPUESTA = 2300
EVENTOREFRESCO = EVENTORESPUESTA+1
TIEMPOREFRESCO = 250

# variables globales para adaptar la pantalla a distintas resoluciones
scale = 1
shift_x = 0
shift_y = 0
xo_resolution = True
presx = 75
presy = 61
clock = pygame.time.Clock()

def wait_events():
    """ Funcion para esperar por eventos de pygame sin consumir CPU """
    global clock
    clock.tick(20)
    return pygame.event.get()


class Zona():
    """Clase para zonas de una imagen.

    La posicion esta dada por una imagen bitmap pintada con un color
    especifico, dado por la clave (valor 0 a 255 del componente rojo).
    """

    def __init__(self,mapa,nombre,claveColor,tipo,posicion,rotacion):
        self.mapa = mapa
        self.nombre = nombre
        self.claveColor = int(claveColor)
        self.tipo = int(tipo)
        self.posicion = (int(int(posicion[0])*scale+shift_x),
                         int(int(posicion[1])*scale+shift_y))
        self.rotacion = int(rotacion)

    def estaAca(self,pos):
        """Devuelve True si la coordenada pos esta en la zona"""
        if pos[0] < XMAPAMAX*scale+shift_x:
            colorAca = self.mapa.get_at((pos[0]-shift_x, pos[1]-shift_y))
            if colorAca[0] == self.claveColor:
                return True
            else:
                return False
        else:
            return False

    def mostrarNombre(self,pantalla,fuente,color,flipAhora):
        """Escribe el nombre de la zona en su posicion"""
        text = fuente.render(self.nombre, 1, color)
        textrot = pygame.transform.rotate(text, self.rotacion)
        textrect = textrot.get_rect()
        textrect.center = (self.posicion[0], self.posicion[1])
        pantalla.blit(textrot, textrect)
	if flipAhora:
            pygame.display.flip()


class Nivel():
    """Clase para definir los niveles del juego.

    Cada nivel tiene un dibujo inicial, los elementos pueden estar
    etiquetados con el nombre o no, y un conjunto de preguntas.
    """

    def __init__(self,nombre):
        self.nombre = nombre
        self.preguntas = list()
        self.indicePreguntaActual = 0
        self.elementosActivos = list()

    def prepararPreguntas(self):
        """Este metodo sirve para preparar la lista de preguntas al azar."""
        random.shuffle(self.preguntas)

    def siguientePregunta(self,listaSufijos,listaPrefijos):
        """Prepara el texto de la pregunta siguiente"""
        self.preguntaActual = self.preguntas[self.indicePreguntaActual]
        self.sufijoActual = random.randint(1,len(listaSufijos))-1
        self.prefijoActual = random.randint(1,len(listaPrefijos))-1
        lineas = listaPrefijos[self.prefijoActual].split("\\")
        lineas.extend(self.preguntaActual[0].split("\\"))
        lineas.extend(listaSufijos[self.sufijoActual].split("\\"))
        self.indicePreguntaActual = self.indicePreguntaActual+1
        if self.indicePreguntaActual == len(self.preguntas):
            self.indicePreguntaActual = 0
        return lineas

    def devolverAyuda(self):
        """Devuelve la linea de ayuda"""
	self.preguntaActual = self.preguntas[self.indicePreguntaActual-1]
        return self.preguntaActual[2].split("\\")

    def mostrarPregunta(self,pantalla,fuente,sufijo,prefijo):
        """Muestra la pregunta en el globito"""
        self.preguntaActual = self.preguntas[self.indicePreguntaActual]
        lineas = prefijo.split("\\")
        lineas.extend(self.preguntaActual[0].split("\\"))
        lineas.extend(sufijo.split("\\"))
        yLinea = 100
        for l in lineas:
            text = fuente.render(l, 1, COLORPREGUNTAS)
            textrect = text.get_rect()
            textrect.center = (XCENTROPANEL,yLinea)
            pantalla.blit(text, textrect)
            yLinea = yLinea + fuente.get_height()
	pygame.display.flip()


class ConozcoEl():
    """Clase principal del juego.

    """

    def mostrarTexto(self,texto,fuente,posicion,color):
        """Muestra texto en una determinada posicion"""
        text = fuente.render(texto, 1, color)
        textrect = text.get_rect()
        textrect.center = posicion
        self.pantalla.blit(text, textrect)

    def cargarZonas(self):
        """Carga las imagenes y los datos de las zonas"""
        self.zonas = self.cargarImagen("zonas.png")
        self.listaZonas = list()
        # falta sanitizar manejo de archivo
        f = open(os.path.join(self.camino_datos,ARCHIVOZONAS),"r")
        linea = f.readline()
        while linea:
            if linea[0] == "#":
                linea = f.readline()
                continue
            [nombreZona,claveColor,posx,posy,rotacion] = \
                linea.strip().split("|")
            nuevaZona = Zona(self.zonas,
                              unicode(nombreZona,'iso-8859-1'),
                              claveColor,1,(posx,posy),rotacion)
            self.listaZonas.append(nuevaZona)
            linea = f.readline()
        f.close()

    def cargarNiveles(self):
        """Carga los niveles del archivo de configuracion"""
        self.listaNiveles = list()
        self.listaPrefijos = list()
        self.listaSufijos = list()
        self.listaCorrecto = list()
        self.listaMal = list()
        self.listaDespedidas = list()
        # falta sanitizar manejo de archivo
        f = open(os.path.join(self.camino_datos,ARCHIVONIVELES),"r")
        linea = f.readline()
        while linea:
            if linea[0] == "#":
                linea = f.readline()
                continue
            if linea[0] == "[":
                # empieza nivel
                nombreNivel = linea.strip("[]\n")
                nuevoNivel = Nivel(nombreNivel)
                self.listaNiveles.append(nuevoNivel)
                linea = f.readline()
                continue
            if linea.find("=") == -1:
                linea = f.readline()
                continue         
            [var,valor] = linea.strip().split("=")
            if var.startswith("Prefijo"):
                self.listaPrefijos.append(
                    unicode(valor.strip(),'iso-8859-1'))
            elif var.startswith("Sufijo"):
                self.listaSufijos.append(
                    unicode(valor.strip(),'iso-8859-1'))
            elif var.startswith("Correcto"):
                self.listaCorrecto.append(
                    unicode(valor.strip(),'iso-8859-1'))
            elif var.startswith("Mal"):
                self.listaMal.append(
                    unicode(valor.strip(),'iso-8859-1'))
            elif var.startswith("Despedida"):
                self.listaDespedidas.append(
                    unicode(valor.strip(),'iso-8859-1'))
            elif var.startswith("Pregunta"):
                [texto,respuesta,ayuda] = valor.split("|")
                nuevoNivel.preguntas.append(
                    (unicode(texto.strip(),'iso-8859-1'),
                     unicode(respuesta.strip(),'iso-8859-1'),
                     unicode(ayuda.strip(),'iso-8859-1')))
            linea = f.readline()
        f.close()
        self.indiceNivelActual = 0
        self.numeroNiveles = len(self.listaNiveles)
        self.numeroSufijos = len(self.listaSufijos)
        self.numeroPrefijos = len(self.listaPrefijos)
        self.numeroCorrecto = len(self.listaCorrecto)
        self.numeroMal = len(self.listaMal)
        self.numeroDespedidas = len(self.listaDespedidas)

    def pantallaAcerca(self):
	global scale, shift_x, shift_y, xo_resolution
	self.pantallaTemp = pygame.Surface(
	    (self.anchoPantalla,self.altoPantalla))
	self.pantallaTemp.blit(self.pantalla,(0,00))
	self.pantalla.fill((0,0,0))
	self.pantalla.blit(self.terron,
			   (int(20*scale+shift_x),
			    int(20*scale+shift_y)))

	f = open(os.path.join(CAMINORECURSOS,
			      CAMINOCOMUN,
			      CAMINODATOS,
			      ARCHIVOCREDITOS),"r")
	yLinea = int(50*scale+shift_y)
	for linea in f:
	    self.mostrarTexto(linea.strip(),
			      self.fuente32,
			      (int(600*scale+shift_x),yLinea),
			      (155,155,155))
	    yLinea = yLinea + int(40*scale)
	f.close()
        self.mostrarTexto("Presiona cualquier tecla para volver",
                          self.fuente32,
                          (int(600*scale+shift_x),
                           int(800*scale+shift_y)),
                          (100,100,100))
	pygame.display.flip()
        while 1:
            for event in wait_events():
                if event.type == pygame.KEYDOWN:
                    self.click.play()
                    self.pantalla.blit(self.pantallaTemp,(0,0))
                    pygame.display.flip()
                    return
                elif event.type == EVENTOREFRESCO:
                    pygame.display.flip()

    def pantallaPres(self):
        """Pantalla con la presentacion de ano internacional de la materia"""
        global scale, shift_x, shift_y, xo_resolution
        self.pantallaTemp = pygame.Surface(
            (self.anchoPantalla,self.altoPantalla))
        self.pantallaTemp.blit(self.pantalla,(0,0))
        self.pantalla.fill((0,0,0))
        self.pantalla.blit(self.presentacion,
                           (int(0*scale+shift_x),
                            int(0*scale+shift_y)))

        # falta sanitizar acceso a archivo
        f = open(os.path.join(CAMINORECURSOS,
                              CAMINOCOMUN,
                              CAMINODATOS,
			      ARCHIVOPRES),"r")
        yLinea = int(0*scale+shift_y)
        for linea in f:
            self.mostrarTexto(linea.strip(),
                              self.fuente32,
                              (int(0*scale+shift_x),yLinea),
                              (155,155,255))
            yLinea = yLinea + int(0*scale)
        f.close()
        self.mostrarTexto("Presiona cualquier tecla para continuar",
                          self.fuente32,
                          (int(600*scale+shift_x),
                           int(830*scale+shift_y)),
                          (100,100,100))
	pygame.display.flip()
        while 1:
            for event in wait_events():
                if event.type == pygame.KEYDOWN:
                    self.click.play()
                    self.pantalla.blit(self.pantallaTemp,(0,0))
                    pygame.display.flip()
                    return
                elif event.type == EVENTOREFRESCO:
                    pygame.display.flip()

    def pantallaInicial(self):
        """Pantalla con el menu principal del juego"""
        global scale, shift_x, shift_y
        self.pantalla.fill((0,0,0))
        self.mostrarTexto("CONOZCO ELEMENTOS QUIMICOS",
                          self.fuente48,
                          (int(600*scale+shift_x),
                           int(80*scale+shift_y)),
                          (255,255,255))
        self.mostrarTexto("Juego",
                          self.fuente48,
                          (int(300*scale+shift_x), int(220*scale+shift_y)),
                          (200,100,100))
        yLista = int(300*scale+shift_y)
        for n in self.listaNiveles:
            self.pantalla.fill((20,20,20),
                               (int(10*scale+shift_x),
                                yLista-int(24*scale),
                                int(590*scale),
                                int(48*scale)))
            self.mostrarTexto(n.nombre,
                              self.fuente40,
                              (int(300*scale+shift_x), yLista),
                              (200,100,100))
            yLista += int(50*scale)
        self.pantalla.fill((20,20,20),
                           (int(10*scale+shift_x),
                            int(801*scale+shift_y),
                            int(590*scale),int(48*scale)))
        self.mostrarTexto("Informacion",
                          self.fuente40,
                          (int(300*scale+shift_x),int(825*scale+shift_y)),
                          (100,200,100))
        self.pantalla.fill((20,20,20),
                           (int(610*scale+shift_x),
                            int(801*scale+shift_y),
                            int(590*scale),int(48*scale)))
        self.mostrarTexto("Salir",
                          self.fuente40,
                          (int(900*scale+shift_x),int(825*scale+shift_y)),
                          (100,200,100))
        pygame.display.flip()
        while 1:
            for event in wait_events():
                if event.type == pygame.KEYDOWN:
                    if event.key == 27: # escape: volver
                        self.click.play()
                        self.elegir_directorio = True
                        return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.click.play()
                    pos = event.pos
                    if pos[1] > 275*scale + shift_y: # zona de opciones
                        if pos[0] < 600*scale + shift_x: # primera columna
                            if pos[1] < 275*scale + shift_y + \
                                    len(self.listaNiveles)*50*scale: # nivel
                                self.indiceNivelActual = \
                                    int((pos[1]-int(275*scale+shift_y))//\
                                            int(50*scale))
                                self.jugar = True
                                return
                            elif pos[1] > 800*scale + shift_y and \
                                    pos[1] < 850*scale + shift_y: # acerca de
                                self.pantallaPres()
				self.pantallaAcerca()
                        else: # segunda columna
                            if pos[1] > 800*scale + shift_y and \
                                    pos[1] < 850*scale+shift_y: # volver
                                self.elegir_directorio = True
                                return
                elif event.type == EVENTOREFRESCO:
                    pygame.display.flip()

    def cargarImagen(self,nombre):
        """Carga una imagen y la escala de acuerdo a la resolucion"""
        global scale, xo_resolution
        if xo_resolution:
            imagen = pygame.image.load( \
                os.path.join(self.camino_imagenes,nombre))
        else:
            imagen0 = pygame.image.load( \
                os.path.join(self.camino_imagenes,nombre))
            imagen = pygame.transform.scale(imagen0,
                          (int(imagen0.get_width()*scale),
                           int(imagen0.get_height()*scale)))
            del imagen0
        return imagen

    def __init__(self):
        """Esta es la inicializacion del juego"""
        global pres_x, pres_y, scale, shift_x, shift_y, xo_resolution
        pygame.init()
        # crear pantalla
        self.anchoPantalla = gtk.gdk.screen_width()
        self.altoPantalla = gtk.gdk.screen_height()
        self.pantalla = pygame.display.set_mode((self.anchoPantalla,
                                                 self.altoPantalla))
        if self.anchoPantalla==1200 and self.altoPantalla==900:
            xo_resolution = True
            scale = 1
            shift_x = 0
            shift_y = 0
	    pres_x = 50
	    pres_y = 50
        else:
            xo_resolution = False
            if self.anchoPantalla/1200.0<self.altoPantalla/900.0:
                scale = self.anchoPantalla/1200.0
                shift_x = 0
                shift_y = int((self.altoPantalla-scale*900)/2)
            else:
                scale = self.altoPantalla/900.0
                shift_x = int((self.anchoPantalla-scale*1200)/2)
                shift_y = 0
        # cargar imagenes generales
        self.camino_imagenes = os.path.join(CAMINORECURSOS,
                                            CAMINOCOMUN,
                                            CAMINOIMAGENES)
        self.bicho = self.cargarImagen("bicho.png")
        self.globito = self.cargarImagen("globito.png")
	self.nave = list()
	self.nave.append(self.cargarImagen("nave1.png"))
	self.nave.append(self.cargarImagen("nave2.png"))
	self.nave.append(self.cargarImagen("nave3.png"))
	self.nave.append(self.cargarImagen("nave4.png"))
	self.nave.append(self.cargarImagen("nave5.png"))
	self.nave.append(self.cargarImagen("nave6.png"))
	self.nave.append(self.cargarImagen("nave7.png"))
        self.presentacion = (self.cargarImagen("presentacion.png"))
	self.terron = (self.cargarImagen("terron.png"))
        # cargar sonidos
        self.camino_sonidos = os.path.join(CAMINORECURSOS,
                                           CAMINOCOMUN,
                                           CAMINOSONIDOS)
        self.click = pygame.mixer.Sound(os.path.join(\
                self.camino_sonidos,"junggle_btn045.wav"))
        self.click.set_volume(0.2)
        # cargar fuentes
        self.fuente48 = pygame.font.Font(os.path.join(CAMINORECURSOS,\
                                                          CAMINOCOMUN,\
                                                          CAMINOFUENTES,\
                                                          "AllCaps.ttf"),
                                         int(48*scale))
        self.fuente40 = pygame.font.Font(os.path.join(CAMINORECURSOS,\
                                                          CAMINOCOMUN,\
                                                          CAMINOFUENTES,\
                                                          "Share-Regular.ttf"),
                                         int(34*scale))
        self.fuente32 = pygame.font.Font(None, int(32*scale))
        self.fuente24 = pygame.font.Font(None, int(24*scale))
        # cursor
        datos_cursor = (
            "..............................  ",
            ".XXXXXXXXXXXXXXXXXXXXXXXXXXXXX. ",
            ".XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.",
            ".XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.",
            ".XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.",
            ".XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.",
            ".XXXXXXXXXXXXXXXXXXXXXXXXXXXXX. ",
            ".XXXXXXXXXXXX.................  ",
            ".XXXXXXXXXXXXX.                 ",
            ".XXXXXXXXXXXXXX.                ",
            ".XXXXXXXXXXXXXXX.               ",
            ".XXXXXXXXXXXXXXXX.              ",
            ".XXXXXXXXXXXXXXXXX.             ",
            ".XXXXXXXXXXXXXXXXXX.            ",
            ".XXXXXXXXXXXXXXXXXXX.           ",
            ".XXXXXXXX.XXXXXXXXXXX.          ",
            ".XXXXXXXX..XXXXXXXXXXX.         ",
            ".XXXXXXXX. .XXXXXXXXXXX.        ",
            ".XXXXXXXX.  .XXXXXXXXXXX.       ",
            ".XXXXXXXX.   .XXXXXXXXXXX.      ",
            ".XXXXXXXX.    .XXXXXXXXXXX.     ",
            ".XXXXXXXX.     .XXXXXXXXXXX.    ",
            ".XXXXXXXX.      .XXXXXXXXXXX.   ",
            ".XXXXXXXX.       .XXXXXXXXXXX.  ",
            ".XXXXXXXX.        .XXXXXXXXXXX. ",
            ".XXXXXXXX.         .XXXXXXXXXXX.",
            ".XXXXXXXX.          .XXXXXXXXXX.",
            ".XXXXXXXX.           .XXXXXXXXX.",
            ".XXXXXXXX.            .XXXXXXXX.",
            " .XXXXXX.              .XXXXXX. ",
            "  .XXXX.                .XXXX.  ",
            "   ....                  ....   ")
        cursor = pygame.cursors.compile(datos_cursor)
        pygame.mouse.set_cursor((32,32), (1,1), *cursor)

    def cargarDirectorio(self):
        """Carga la informacion especifica de un directorio"""
        self.camino_imagenes = os.path.join(CAMINORECURSOS,CAMINOLAMINA)
        self.camino_datos = os.path.join(CAMINORECURSOS,CAMINOLAMINA)
        self.fondo = self.cargarImagen("lamina.png")
        self.cargarZonas()
        self.cargarNiveles()

    def mostrarGlobito(self,lineas):
        """Muestra texto en el globito"""
        global scale, shift_x, shift_y
        self.pantalla.blit(self.globito,
                           (int(XMAPAMAX*scale+shift_x),
                            int(YGLOBITO*scale+shift_y)))
        yLinea = int(YGLOBITO*scale) + shift_y + \
            self.fuente32.get_height()*3
        for l in lineas:
            text = self.fuente32.render(l, 1, COLORPREGUNTAS)
            textrect = text.get_rect()
            textrect.center = (int(XCENTROPANEL*scale+shift_x),yLinea)
            self.pantalla.blit(text, textrect)
            yLinea = yLinea + self.fuente32.get_height() + int(10*scale)
	pygame.display.flip()

    def borrarGlobito(self):
        """ Borra el globito, lo deja en blanco"""
        global scale, shift_x, shift_y
        self.pantalla.blit(self.globito,
                           (int(XMAPAMAX*scale+shift_x),
                            int(YGLOBITO*scale+shift_y)))
# agrego self.pantalla.blit para nave ana
    def correcto(self):
        """Muestra texto en el globito cuando la respuesta es correcta"""
        global scale, shift_x, shift_y
	self.pantalla.blit(self.nave[self.avanceNivel],
			   (int(XNAVE*scale+shift_x),
			     int(YNAVE*scale+shift_y)))
        self.correctoActual = random.randint(1,self.numeroCorrecto)-1
        self.mostrarGlobito([self.listaCorrecto[self.correctoActual]])
        self.esCorrecto = True
        pygame.time.set_timer(EVENTORESPUESTA,TIEMPORESPUESTA)
        
    def mal(self):
        """Muestra texto en el globito cuando la respuesta es incorrecta"""
        self.malActual = random.randint(1,self.numeroMal)-1
        self.mostrarGlobito([self.listaMal[self.malActual]])
        self.esCorrecto = False
        self.nRespuestasMal += 1
        pygame.time.set_timer(EVENTORESPUESTA,TIEMPORESPUESTA)

    def esCorrecta(self,nivel,pos):
        """Devuelve True si las coordenadas cliqueadas corresponden a la
        respuesta correcta
        """
        respCorrecta = nivel.preguntaActual[1]
        encontrado = False
        for d in self.listaZonas:
            if d.nombre.startswith(respCorrecta):
                encontrado = True
                break
        if d.estaAca(pos):
            return True
        else:
            return False

    def jugarNivel(self):
        """Juego principal de preguntas y respuestas"""
        self.nivelActual = self.listaNiveles[self.indiceNivelActual]
        self.avanceNivel = 0
        self.nivelActual.prepararPreguntas()
        self.pantalla.fill((100,20,20),
                           (int(975*scale+shift_x),
                            int(26*scale+shift_y),
                            int(200*scale),
                            int(48*scale)))
        self.mostrarTexto("Terminar",
                          self.fuente40,
                          (int(1075*scale+shift_x),
                           int(50*scale+shift_y)),
                          (255,155,155))
        pygame.display.flip()
        # presentar pregunta inicial
        self.lineasPregunta = self.nivelActual.siguientePregunta(\
                self.listaSufijos,self.listaPrefijos)
        self.mostrarGlobito(self.lineasPregunta)
        self.nRespuestasMal = 0
        # leer eventos y ver si la respuesta es correcta
        while 1:
            for event in wait_events():
                if event.type == pygame.KEYDOWN:
                    if event.key == 27: # escape: salir
                        self.click.play()
                        pygame.time.set_timer(EVENTORESPUESTA,0)
                        return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.click.play()
                    if self.avanceNivel < TOTALAVANCE:
                        if event.pos[0] < XMAPAMAX*scale+shift_x: # zona mapa
                            self.borrarGlobito()
                            if self.esCorrecta(self.nivelActual,
                                               event.pos):
                                self.correcto()
                            else:
                                self.mal()
                        elif event.pos[0] > 975*scale+shift_x and \
                                event.pos[0] < 1175*scale+shift_x and \
                                event.pos[1] > 25*scale+shift_y and \
                                event.pos[1] < 75*scale+shift_y: # terminar
                            return
                elif event.type == EVENTORESPUESTA:
                    pygame.time.set_timer(EVENTORESPUESTA,0)
                    if self.esCorrecto:
                        if self.avanceNivel == TOTALAVANCE:
                            return
                        self.avanceNivel = self.avanceNivel + 1
                        if self.avanceNivel == TOTALAVANCE: # fin
                            self.lineasPregunta =  self.listaDespedidas[\
                                random.randint(1,self.numeroDespedidas)-1]\
                                .split("\\")
                            self.mostrarGlobito(self.lineasPregunta)
                            pygame.time.set_timer(
                                EVENTORESPUESTA,TIEMPORESPUESTA)
                        else: # pregunta siguiente
                            self.lineasPregunta = \
                                self.nivelActual.siguientePregunta(\
                                self.listaSufijos,self.listaPrefijos)
                            self.mostrarGlobito(self.lineasPregunta)
                            self.nRespuestasMal = 0
                    else:
                        if self.nRespuestasMal >= 2: # ayuda
                            self.mostrarGlobito(
                                self.nivelActual.devolverAyuda())
                            self.nRespuestasMal = 0
                            pygame.time.set_timer(
                                EVENTORESPUESTA,TIEMPORESPUESTA)
                        else: # volver a preguntar
                            self.mostrarGlobito(self.lineasPregunta)
                elif event.type == EVENTOREFRESCO:
                    pygame.display.flip()

    def principal(self):
        """Este es el loop principal del juego"""
        global scale, shift_x, shift_y
        pygame.time.set_timer(EVENTOREFRESCO,TIEMPOREFRESCO)
        while 1:
            self.cargarDirectorio()
            while 1:
                # pantalla inicial de juego
                self.elegir_directorio = False
                self.pantallaInicial()
                if self.elegir_directorio: # volver a seleccionar mapa
                    sys.exit()
                # dibujar fondo y panel
                self.pantalla.blit(self.fondo, (shift_x, shift_y))
                self.pantalla.fill(COLORPANEL,
                                   (int(XMAPAMAX*scale+shift_x),shift_y,
                                    int(DXPANEL*scale),int(900*scale)))
                self.pantalla.blit(self.bicho,
                                   (int(XBICHO*scale+shift_x),
                                    int(YBICHO*scale+shift_y)))
                # mostrar pantalla
                pygame.display.flip()
                # ir al juego
                self.jugarNivel()
 

def main():
    juego = ConozcoEl()
    juego.principal()


if __name__ == "__main__":
    main()
