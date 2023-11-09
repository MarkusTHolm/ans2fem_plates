import os

# Print files in current directory
print("List of .cdb files in the current directory:")
files = [f for f in os.listdir('.') if os.path.isfile(f)]
cdb_flag = 0
for file in files:
    fileType = file.split('.')[-1]
    if fileType == 'cdb':
        print(f"   {file}")
        cdb_flag = 1
if cdb_flag == 0:
    print("ERROR: No .cdb files in the current directory")
    os.system("pause")
    exit()

# Insert input file
inputFile = input("Enter ANSYS archived output file (<filename>): \n")
with open(inputFile) as f:
    lines = f.readlines()

def read_block_line(line):
    """ Read numbers from a line in the ANSYS 'block' format"""
    num_list = []
    for num in line.strip().split(' '):
        if num != '':
            num_list.append(float(num.split(',')[0]))
    return num_list

# Initialize
nodes = []
elements = []
matprops = []
secdata = []
thickness = []
ndisp = []
nforce = []
surface_loads = []
data = {}
data["F"] = []
data["D"] = []
data["SFE"] = []

for i, line in enumerate(lines):
    line = line.split("\n")[0]                  # Remove \n from line
    line = line.strip()

    split_lines = line.split(',')
    keyword = split_lines[0]
    
    # Element type
    if keyword == "ET":
        data["ET"] = f'ET,{split_lines[1]},{split_lines[2]}'

    # Nodal coordinates
    if keyword == "NBLOCK":
        nnodes = int(split_lines[3].strip())
        for j in range(1, nnodes+1):
            node_line = lines[i+1+j]
            nums = read_block_line(node_line)

            match len(nums):
                case 4:
                    nodes.append(f"N, {int(nums[0])}, {nums[3]}, 0, 0")
                case 5:
                    nodes.append(f"N, {int(nums[0])}, {nums[3]}, {nums[4]}, 0")
                case 6:
                    nodes.append(f"N, {int(nums[0])}, {nums[3]}, {nums[4]}, {nums[5]}")
    
        data["NODES"] = nodes
    
    # Element numbering
    if keyword == "EBLOCK":
        nelements = int(split_lines[3].strip())
        for j in range(1, nelements+1):
            elem_line = lines[i+1+j]
            nums = read_block_line(elem_line)
            nums = [int(n) for n in nums]   # Convert numbers to integers
            
            elements.append(f"EN, {nums[-5]}, {nums[-4]}, {nums[-3]}, {nums[-2]}, {nums[-1]}")
    
        data["ELEMENTS"] = elements
    
    # Material data
    if keyword == "MPDATA":
        if split_lines[3].strip() in ["EX", "PRXY"]:
             matprops.append(f"MP, {split_lines[3]}, "
                             f"{int(split_lines[4])}, "
                             f"{float(split_lines[6])}")
        
        data["MP"] = matprops

    # Section ID
    if keyword == "SECTYPE":
        secdata.append(f"SECTYPE, {int(split_lines[1])}, {split_lines[2]}")
        split_line_p1 = lines[i+1].split('\n')[0].split(",")
        split_line_p2 = lines[i+2].split('\n')[0].split(",")
        num = read_block_line(lines[i+3])
        secdata.append(f"SECOFFSET, {split_line_p1[1]}")
        thk, matid, orientation, integration_points = num[0], int(num[1]), num[2], int(num[3])
        secdata.append(f"SECDATA, {thk}, {matid}, {orientation}, {integration_points}")
        thickness.append(f"R, {matid}, {thk}")

    # Nodal displacements constraints
    if keyword == "D":
        ndisp.append(f"D, {int(split_lines[1])}, {split_lines[2]}, "
                     f"{float(split_lines[3])}")
        
    # Nodal forces
    if keyword == "F":
        nforce.append(f"F, {int(split_lines[1])}, {split_lines[2]}, "
                      f"{float(split_lines[3])}")

    # Surface Loads
    if keyword == "SFEBLOCK":
        nsfe = int(split_lines[3].strip())
        for j in range(1, 2*nsfe + 1, 2):
            sfe_line1 = lines[i+1+j]            
            sfe_line2 = lines[i+2+j]
            num1 = read_block_line(sfe_line1)
            num2 = read_block_line(sfe_line2)

            surface_loads.append(f"SFE, {int(num1[0])}, {int(num2[1])}, "
                                 f"PRES, {num2[3]}, {num1[3]}")
    
        data["SFE"] = surface_loads

# Store nodal boundary conditions
data["D"] = ndisp
data["F"] = nforce
data["SECDATA"] = secdata
data["R"] = thickness

clean_lines = []
clean_lines.append("/PREP7")
clean_lines.append("")
clean_lines.append("/TITLE, ..")
clean_lines.append("")
clean_lines.append(data["ET"])
clean_lines.append("")
clean_lines.append("! Define node coordinates: N, node #, x-coor, y-coor, z-coor")
for node in data["NODES"]:
    clean_lines.append(node)
clean_lines.append("")
clean_lines.append("! Define element numbering: EN, element #, nodal list")
clean_lines.append("MAT, 1")
clean_lines.append("REAL, 1")
clean_lines.append("")
for elem in data["ELEMENTS"]:
    clean_lines.append(elem)
clean_lines.append("")
for mp in data["MP"]:
    clean_lines.append(mp)
clean_lines.append("")
for sd in data["SECDATA"]:
    clean_lines.append(sd)
clean_lines.append("")
for thk in data["R"]:
    clean_lines.append(thk)
clean_lines.append("")
for disp in data["D"]:
    clean_lines.append(disp)
clean_lines.append("")
for force in data["F"]:
    clean_lines.append(force)
clean_lines.append("")
for sfe in data["SFE"]:
    clean_lines.append(sfe)
clean_lines.append("FINISH")

outputFile = f"{inputFile.split('.')[0]}.fem"
with open(outputFile, 'w') as f:   
    for line in clean_lines:
        f.write(f"{line}\n")

print(f"Succesfully created: {outputFile}")
os.system("pause")
