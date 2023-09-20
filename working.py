import oom_kicad
import oom_markdown
import oom_svg

#process
#  locations set in working_parts.ods 
#  export to working_parts.csv
#  put components on the right side of the board
#  run this script

def main(**kwargs):
    #place_parts(**kwargs)
    
    file_svg = "working_samples_angled_line.svg"
    file_svg = "working_samples_bezier.svg"
    file_svg = "working_samples_letter_a.svg"
    file_svg = "working_samples_arrow.svg"
    file_svg = "working_samples_spiral.svg"
    file_svg = "working_samples_seven_single.svg"
    file_svg = "working_samples_seven_multiple.svg"
    file_svg_out = file_svg.replace(".svg", "_points.svg")

    points = get_points_along_svg(file_svg=file_svg, n_points=30, **kwargs)
    points = get_points_along_svg_with_angle(file_svg=file_svg, n_points=200, **kwargs)

    kwargs["format"] = "mm"

    save_points_as_svg(file_out=file_svg_out, points=points, **kwargs)
    #oom_svg.svg_make_pdf(file=file_svg_out, **kwargs)

    parts = []
    for i, point in enumerate(points):
        reference = f"L{i}"
        position_x = point["x"]
        position_y = -point["y"]
        rotation =  point["angle"] +45
        parts.append({"reference":reference, "position_x":position_x, "position_y":position_y, "rotation":rotation})

        

    # convert to kicad spots
    board_file = "kicad/current_version/working/working.kicad_pcb"
    oom_kicad.kicad_set_components(board_file=board_file, parts=parts, corel_pos=False, **kwargs)


    make_readme(**kwargs)
    
    

def make_readme(**kwargs):
    oom_markdown.generate_readme_project(**kwargs)
    
#take component positions from working_parts.csv and place them in working.kicad_pcb
def place_parts(**kwargs):
    board_file = "kicad/current_version/working/working.kicad_pcb"
    parts_file = "working_parts.csv"

    #load csv file
    import csv
    with open(parts_file, 'r') as f:
        reader = csv.DictReader(f)
        parts = [row for row in reader]

   
    oom_kicad.kicad_set_components(board_file=board_file, parts=parts, corel_pos=True, **kwargs)

def get_points_along_svg_with_angle(**kwargs):
    file_svg = kwargs.get('file_svg', None)
    n_points = kwargs.get('n_points', 10)
    format = kwargs.get('format', "mm")
    if file_svg is None:
        print("No file_svg given")
        return None
    import svgpathtools as svg
    path, attributes = svg.svg2paths(file_svg)
    #print(path)
    #print(attributes)
    #print(path[0].length())
    points = []
    #if path isn't an array make it one
    num_paths = len(path)
    points_per = int(n_points/num_paths)
    if type(path) != list:
        path = [path]
    for p in path:
        i=0
        for i in range(points_per):
            point_progress = i/points_per
            x = p.point(point_progress).real
            y = p.point(point_progress).imag
            #a little before and after the point
            point_before = p.point((i-0.25)/points_per)
            point_after = p.point((i+0.25)/points_per)
            #use before and after to calculate angle
            #get the vector of the line segment
            vector = point_after-point_before
            #get the angle of the vector
            import cmath
            angle = cmath.phase(vector)
            #make angle a float
            angle = angle.real
            #convert to degrees
            angle = angle*180/3.14159
            #print(angle)
            point_add = {}
            point_add["x"] = x
            point_add["y"] = y
            point_add["angle"] = -angle
            points.append(point_add)
    #print(points)
    #turn points into mm by dividing each coord by 100
    if format == "mm":
        for point in points:
            point["x"] = point["x"]/100
            point["y"] = point["y"]/100

    
    return points

def get_points_along_svg(**kwargs):
    file_svg = kwargs.get('file_svg', None)
    n_points = kwargs.get('n_points', 10)
    format = kwargs.get('format', "mm")
    if file_svg is None:
        print("No file_svg given")
        return None
    import svgpathtools as svg
    path, attributes = svg.svg2paths(file_svg)
    #print(path)
    #print(attributes)
    #print(path[0].length())
    points = []
    for i in range(n_points):
        points.append(path[0].point(i/n_points))
    #convert to dict
    points = [{"x":point.real, "y":point.imag} for point in points]
    #print(points)
    #turn points into mm by dividing each coord by 100
    if format == "mm":
        for point in points:
            point["x"] = point["x"]*100
            point["y"] = point["y"]*100

    return points

def save_points_as_svg(**kwargs):
    file_out = kwargs.get('file_out', None)
    format = kwargs.get('format', "mm")
    import copy 
    points = kwargs.get('points', None)
    points = copy.deepcopy(points)
    if file_out is None:
        print("No file_out given")
        return None
    if points is None:
        print("No points given")
        return None
    import svgwrite
    dwg = svgwrite.Drawing(file_out, profile='tiny')
    
    if format == "mm":
        # in dict with x as "x"
        for point in points:
            point["x"] = point["x"]/100
            point["y"] = point["y"]/100


    for point in points:
        #make the circle 3x3 mm and red
        dwg.add(dwg.circle(center=(point["x"], point["y"]), r=30, stroke='red', fill='red'))
    dwg.save()




if __name__ == '__main__':
    main()