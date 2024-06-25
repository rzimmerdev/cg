#define MAX_LIGHTS 10

varying vec2 out_texture;
uniform sampler2D samplerTexture;

uniform vec3 cameraPos;

uniform float ambientCoefficient; // k_a
uniform vec3 ambientLight; // I_a

uniform int numLights;
uniform vec3 lightPos[MAX_LIGHTS]; // Array of light positions
uniform vec3 lightColor[MAX_LIGHTS]; // Array of light colors
uniform float diffuseCoefficient; // k_d
uniform float specularCoefficient; // k_s
uniform float shininess; // n

varying vec3 out_normal;
varying vec3 out_position;


void main() {
    vec4 textureColor = texture2D(samplerTexture, out_texture);
    vec3 viewDir = normalize(cameraPos - out_position);
    vec3 normal = normalize(out_normal);

    // Ambient lighting
    vec3 ambient = (ambientCoefficient * ambientLight); // k_a * I_a

    vec3 diffuse = vec3(0.0);
    vec3 specular = vec3(0.0);

    for (int i = 0; i < numLights; ++i) {
        vec3 lightDir = normalize(lightPos[i] - out_position);
        vec3 reflectDir = reflect(-lightDir, normal);

        // Diffuse lighting
        float diff = max(dot(normal, lightDir), 0.0);
        diffuse += diffuseCoefficient * diff * lightColor[i]; // k_d * (N * L) * I_d

        // Specular lighting
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
        specular += specularCoefficient * spec * lightColor[i]; // k_s * (V * R)^n * I_s

        // Distance attenuation
        float distance = length(lightPos[i] - out_position);
        float attenuation = 1.0 / (distance * distance);

        diffuse *= attenuation;
        // specular *= attenuation;
    }

    vec3 resultColor = clamp(ambient + diffuse + specular, 0.0, 1.0); // Add the texture color
    gl_FragColor = textureColor * vec4(resultColor, 1.0);
}