from estructuras import ColaPrioridadTurnos
 
 
def verificar(nombre, obtenido, esperado):
    estado = "OK " if obtenido == esperado else "ERROR"
    print(f"[{estado}] {nombre}: {obtenido}  (esperado: {esperado})")
 
 
c = ColaPrioridadTurnos()
c.insertar("laura", 3)
c.insertar("jose", 2)
c.insertar("carlos", 1)
c.insertar("ana", 1)
 
verificar("posicion de ana", c.posicion("ana"), 2)
verificar("contiene carlos", c.contiene("carlos"), True)
verificar("extraer_con_datos", c.extraer_con_datos(), (1, 2, "carlos"))
 
c.reinsertar(1, 2, "carlos")
verificar("orden tras reinsertar", c.listar_ordenado(), ["carlos", "ana", "jose", "laura"])
 
verificar("eliminar jose", c.eliminar("jose"), (2, 1, "jose"))
verificar("eliminar inexistente", c.eliminar("nadie"), None)
 
c.reemplazar("laura", "laura2")
verificar("orden tras reemplazar", c.listar_ordenado(), ["carlos", "ana", "laura2"])
 