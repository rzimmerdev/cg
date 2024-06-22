#define MAX_LIGHTS 10

uniform vec4 color;
varying vec2 out_texture;
uniform sampler2D samplerTexture;

uniform vec3 cameraPos;

uniform vec3 ambientColor; // k_a
uniform vec3 ambientLightIntensity; // I_a

uniform vec3 lightPos[MAX_LIGHTS]; // Array of light positions
uniform vec3 lightColor[MAX_LIGHTS]; // Array of light colors
uniform vec3 diffuseColor; // k_d
uniform vec3 specularColor; // k_s
uniform float shininess; // n

varying vec3 fragNormal; // Pass this from the vertex shader

void main() {
    vec4 textureColor = texture2D(samplerTexture, out_texture);
    vec3 fragPos = gl_FragCoord.xyz;

    vec3 viewDir = normalize(cameraPos - fragPos);
    vec3 normal = normalize(fragNormal); // Use the varying normal from the vertex shader

    // Ambient lighting
    vec3 ambient = ambientColor * ambientLightIntensity; // k_a * I_a

    vec3 diffuse = vec3(0.0);
    vec3 specular = vec3(0.0);

    for (int i = 0; i < MAX_LIGHTS; ++i) {
        vec3 lightDir = normalize(lightPos[i] - fragPos);
        vec3 reflectDir = reflect(-lightDir, normal);

        // Diffuse lighting
        float diff = max(dot(normal, lightDir), 0.0);
        diffuse += diff * diffuseColor * lightColor[i]; // k_d * I_d

        // Specular lighting
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
        specular += spec * specularColor * lightColor[i]; // k_s * I_s

        // Distance attenuation
        float distance = length(lightPos[i] - fragPos);
        float attenuation = 1.0 / (distance * distance);
        
        diffuse *= attenuation;
        specular *= attenuation;
    }

    vec3 resultColor = ambient + diffuse + specular;
    gl_FragColor = vec4(resultColor * textureColor.rgb, textureColor.a);
}
