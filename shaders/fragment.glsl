#version 330 core
out vec4 FragColor;

// Texture
uniform sampler2D texture_data;

// Texture coordinates
in vec2 TexCoord;

void main()
{
    FragColor = texture(texture_data, TexCoord);
}