
class InformeLider:
    lider = ""
    votantes = 0
    pendientes = 0
    asistieron_presencial = 0
    asistieron_no_presencial = 0
    no_asistieron = 0

    def __init__(self, lider, votantes, pendientes, asis_pres, asis_no_pres, no_asis):
        self.lider = lider
        self.votantes = votantes
        self.pendientes = pendientes
        self.asistieron_presencial = asis_pres
        self.asistieron_no_presencial = asis_no_pres
        self.no_asistieron = no_asis