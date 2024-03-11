from pathlib import Path


from viktor import ViktorController, Color
from viktor.parametrization import ViktorParametrization, Text, TextField, NumberField, DateField,LineBreak, ColorField
from viktor.views import GeometryView, GeometryResult, PDFView, PDFResult
from viktor.geometry import Group, Material, SquareBeam, Vector, Point, Line
from viktor.external.word import render_word_file, WordFileTag, WordFileImage
from viktor.utils import convert_word_to_pdf
from viktor.result import DownloadResult
import math


class Parametrization(ViktorParametrization):
    intro = Text("# 3D model of Concrete Corbel\n This app parametrically designs and visualizes a 3D model of a corbel")

    txt_corbel = Text('### Geometry Input')  # texts can be used for explanation in the user-interface

    project_name = TextField("Project Name","", default = 'P 001')
    engineer_name = TextField("Author","", default = 'Engineer 1')
    element_name = TextField("Element Name","", default = 'corbel 1.0')
    date = DateField("Date")
    lb1 = LineBreak()
      
   
    column_width = NumberField("Column Size", min=50, default=80, suffix='cm')
    #beam_width = NumberField("Beam Width", min=20, default=30, suffix='cm')
    #beam_height = NumberField("Beam Height", min=20, default=50, suffix='cm')
    
    corbel_height = NumberField("Corbel Height", min=20, max=100, default=65, suffix='cm', variant='slider')
    corbel_width = NumberField("Corbel Width", min=10, max = 80, default=30, suffix='cm', variant='slider')
    pad_offset = NumberField("Pad Offset", min=0, max = 15, default=5, suffix='cm')
    lb2 = LineBreak()

    V = NumberField("Vertical Force", min = 0, default=250, suffix='kN')
    H = NumberField("Horizontal Force", default=85, suffix='kN')

    #static data
    #pad_offset = NumberField(int = 10)


"""   
class Controller(ViktorController):
    label = '3D Geometry'
    parametrization = Parametrization()

     """

class Controller(ViktorController):

    label = 'Report'
    parametrization = Parametrization()

    def generate_word_document(self, params):

        As1, As2, conc_grade, steel_grade = self.calc_corbel(params) #in cm2
       
        
        ac, hc, check = self.check_corbel(params)

        # Create emtpy components list to be filled later
        components = []

        # Fill components list with data
        components.append(WordFileTag("Project_name", params.project_name))
        components.append(WordFileTag("engineer_name", params.engineer_name))
        components.append(WordFileTag("element_name", params.element_name))
        components.append(WordFileTag("date", str(params.date))) # Convert date to string format

        components.append(WordFileTag("concrete_grade", conc_grade))
        components.append(WordFileTag("steel_grade", steel_grade))
        components.append(WordFileTag("ac", ac))
        components.append(WordFileTag("hc", hc))
        components.append(WordFileTag("check", check))

        components.append(WordFileTag("As1", (round(As1,2), ' cm2')))
        components.append(WordFileTag("As2", (round(As2,2), ' cm2')))

        # Get path to template and render word file
        template_path = Path(__file__).parent / "files" / "Template.docx"
        with open(template_path, 'rb') as template:
            word_file = render_word_file(template, components)

        return word_file

    @GeometryView("3D", duration_guess=1)
    def visualize_corbel(self, params, **kwargs):

        # Create an empty group to hold all the geometry
        geometry_group = Group([])


        # Create materials
        mat_base = Material('Base', color=Color.black(), opacity=0.25)
        mat_column = Material('Column', color=Color.black(), opacity=0.5)
        mat_corbel = Material('Corbel', color=Color.black(), opacity = 0.75)
        mat_pad = Material('Elastomeric Pad', color=Color.blue(), opacity=0.5)
        #mat_force = Material('Force Vector', color=Color.red())

        # ===============================
        # Draw environment and geometry
        # ===============================
        
        ### EVERYTHING in cm!

        env_size = 200 #cm

        # Draw base
        base = SquareBeam(env_size, env_size, env_size/5000, material=mat_base)
        geometry_group.add([base])

        # Draw column

        column = SquareBeam(params.column_width, params.column_width, env_size, material=mat_column)
        column.translate(Vector(0,0,(env_size/2)))
        # Draw corbel geometry with 0,0 at column base center

        corbel = SquareBeam(params.corbel_height, params.column_width/2, params.corbel_width, material=mat_corbel)
        corbel.rotate(-math.pi/2, direction = [0,1,0])
        corbel.translate(Vector((params.column_width/2 + params.corbel_width/2),0,(env_size/2)))
        #params.corbel_width+params.column_width/2
        # Draw elastomeric pad geometry with 0,0 at column base center

        #pad_offset = 10 #cm
        pad_x = (params.corbel_width*0.5 - params.pad_offset) #cm
        pad_y = (params.column_width/2 - params.pad_offset*2) #cm
        pad_z = 2 #cm
        

        pad = SquareBeam(pad_x, pad_y, pad_z, material=mat_pad)
        pad.translate(Vector((params.column_width/2 + params.corbel_width*3/4), 0, (env_size/2 + params.corbel_height/2)))

        # Add created geometries to geometry group
        geometry_group.add([column, corbel, pad])

       
        return GeometryResult(geometry_group)
   
    @PDFView("PDF viewer", duration_guess=5)
    def pdf_view(self, params, **kwargs):
        word_file = self.generate_word_document(params)

        with word_file.open_binary() as f1:
            pdf_file = convert_word_to_pdf(f1)

        return PDFResult(file=pdf_file)

    @staticmethod
    def calc_corbel(params):
        
        # calculation per Schneider 20. [5.124] eqs 5.11 and 5.24
        conc_grade = 'C50/60'
        steel_grade = 'B500B'

        fck = 50 #50Mpa = 5kN/cm2 for C50/60 concrete
        fy = 500
        fyd = 500/1.15 
        Vrd = (0.5*(0.7-fck/200)*(params.column_width*10/2)*(params.corbel_height*10)*fck/1.50)/1000 #calc conc. strut with V_Rdmax = 0,5*(0,7-fck/200)*b*z*fck/gammaC (in KN)
        
        cover = 5 #5cm concrete cover
        d = params.corbel_height - cover
        ac = params.corbel_width - params.pad_offset #cm
        z0 = d*(1-0.4*(params.V/Vrd)) #cm

        Zed = params.V*(ac/z0) + params.H*((cover+z0)/z0) #units in cm

        As1 = (Zed/fyd)*100 #
        As2 = As1*0.5 #in cm2


        return [As1, As2, conc_grade, steel_grade]	
               
 
    def check_corbel(self,params):
        
        ac = params.corbel_width - params.pad_offset #cm
        hc = params.corbel_height

        check = ''
        if ac/hc <= 0.5:
            check = 'True'
        else:
            check = 'False'

        return [ac, hc, check]


    def download_word_file(self, params, **kwargs):
        word_file = self.generate_word_document(params)

        return DownloadResult(word_file, "Report.docx")
    

