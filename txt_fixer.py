import os

LABEL_DIR = "labels"

def unify_dataset():
    if not os.path.exists(LABEL_DIR):
        print(f"Error: Could not find '{LABEL_DIR}' folder.")
        return

    txt_files = [f for f in os.listdir(LABEL_DIR) if f.endswith('.txt')]
    converted_files_count = 0

    for txt_file in txt_files:
        file_path = os.path.join(LABEL_DIR, txt_file)
        
        with open(file_path, 'r') as f:
            lines = f.readlines()

        new_lines = []
        was_modified = False

        for line in lines:
            parts = line.strip().split()
            if not parts:
                continue

            class_id = parts[0]
            coords = [float(x) for x in parts[1:]]

            # If it has more than 4 coordinates, it's a Polygon
            if len(coords) > 4:
                was_modified = True
                
                # Extract all X and Y coordinates
                x_coords = coords[0::2] # Evens are X
                y_coords = coords[1::2] # Odds are Y
                
                # Find the extreme edges of the polygon to form a box
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)
                
                # Convert to YOLOv8 Bounding Box format (Center X, Center Y, Width, Height)
                x_center = (x_min + x_max) / 2.0
                y_center = (y_min + y_max) / 2.0
                width = x_max - x_min
                height = y_max - y_min
                
                # Ensure values don't accidentally exceed image bounds (0.0 to 1.0)
                x_center = max(0.0, min(1.0, x_center))
                y_center = max(0.0, min(1.0, y_center))
                width = max(0.0, min(1.0, width))
                height = max(0.0, min(1.0, height))

                new_lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
            
            # If it has exactly 4 coordinates, it's already a YOLOv8 Bounding Box
            elif len(coords) == 4:
                new_lines.append(line)
            else:
                print(f"Warning: Corrupted line in {txt_file}. Ignoring.")

        # Overwrite the file only if we actually changed a polygon
        if was_modified:
            with open(file_path, 'w') as f:
                f.writelines(new_lines)
            converted_files_count += 1

    print(f"Dataset Unification Complete!")
    print(f"Scanned {len(txt_files)} label files.")
    print(f"Successfully converted {converted_files_count} polygon files into standard bounding boxes.")

if __name__ == "__main__":
    unify_dataset()