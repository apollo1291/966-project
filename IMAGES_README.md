# Required PNG Images

The application now displays images instead of text for the example objects. You need to place the following PNG files in the `public/` directory:

## Required Filenames

```
circle_red_solid_big.png
circle_red_solid_small.png
circle_red_striped_big.png
circle_red_striped_small.png
circle_blue_solid_big.png
circle_blue_solid_small.png
circle_blue_striped_big.png
circle_blue_striped_small.png
square_red_solid_big.png
square_red_solid_small.png
square_red_striped_big.png
square_red_striped_small.png
square_blue_solid_big.png
square_blue_solid_small.png
square_blue_striped_big.png
square_blue_striped_small.png
```

## Image Specifications

- **Format**: PNG
- **Naming**: `{shape}_{color}_{fill}_{size}.png`
- **Location**: `output_images/` directory (in the public folder)
- **Size**: Recommended maximum width of 150px (CSS will scale down if larger)

Each image should visually represent the corresponding combination of features:
- **Shapes**: circle, square
- **Colors**: red, blue
- **Fills**: solid, striped
- **Sizes**: big, small
