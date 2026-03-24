import os

LABEL_DIR = "labels"
TARGET_CLASS_ID = "0"  # We force every label to be '0' (since dots are our only class)

def unify_dataset():
    if not os.path.exists(LABEL_DIR):
        print(f"Error: Could not find '{LABEL_DIR}' folder.")
        return

    txt_files = [f for f in os.listdir(LABEL_DIR) if f.endswith('.txt')]
    fixed_count = 0

    for txt_file in txt_files:
        file_path = os.path.join(LABEL_DIR, txt_file)
        
        with open(file_path, 'r') as f:
            lines = f.readlines()

        new_lines = []
        needs_fixing = False

        for line in lines:
            parts = line.strip().split()
            if not parts:
                continue

            # Check if the original class ID was something other than 0
            original_class_id = parts[0]
            if original_class_id != TARGET_CLASS_ID:
                needs_fixing = True

            # Get the coordinates (everything after the class ID)
            coords = [float(x) for x in parts[1:]]

            # Scenario A: It's a Polygon (more than 4 coordinates)
            if len(coords) > 4:
                needs_fixing = True
                
                # Extract X and Y coordinates
                x_coords = coords[0::2] 
                y_coords = coords[1::2] 
                
                # Find the edges of the polygon to draw a box around it
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)
                
                # Convert to standard YOLO center-width-height format
                x_center = (x_min + x_max) / 2.0
                y_center = (y_min + y_max) / 2.0
                width = x_max - x_min
                height = y_max - y_min
                
                # Ensure values stay within image boundaries (0.0 to 1.0)
                x_center = max(0.0, min(1.0, x_center))
                y_center = max(0.0, min(1.0, y_center))
                width = max(0.0, min(1.0, width))
                height = max(0.0, min(1.0, height))

                # Add the line with our forced '0' class ID
                new_lines.append(f"{TARGET_CLASS_ID} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
            
            # Scenario B: It's already a Bounding Box (exactly 4 coordinates)
            elif len(coords) == 4:
                x_center, y_center, width, height = coords
                # We rewrite it just to guarantee the class ID is '0' and formatting is clean
                new_lines.append(f"{TARGET_CLASS_ID} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
            else:
                print(f"Warning: Ignored corrupted line in {txt_file}: {line.strip()}")

        # If any line in the file was a polygon OR had a wrong class ID, we overwrite the file
        if needs_fixing:
            with open(file_path, 'w') as f:
                f.writelines(new_lines)
            fixed_count += 1

    print(f"✅ Dataset Unification Complete!")
    print(f"Scanned {len(txt_files)} label files.")
    print(f"Fixed {fixed_count} files (Converted polygons & forced class IDs to {TARGET_CLASS_ID}).")

if __name__ == "__main__":
    unify_dataset()