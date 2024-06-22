uniform vec4 color;
varying vec2 out_texture;
uniform sampler2D samplerTexture;

uniform vec3 lightPos;
uniform vec3 cameraPos;

uniform vec3 ambientColor;
uniform vec3 diffuseColor;
uniform vec3 specularColor;
uniform float shininhess;

void main() {
    vec4 textureColor = texture2D(samplerTexture, out_texture);
    vec3 fragPos = gl_FragCoord.xyz;

    lightPos = cameraPos;
    vec3 lightDir = normalize(lightPos - fragPos);
    vec3 viewDir = normalize(cameraPos - fragPos);

    vec3 normal = normalizeI(gl_FronFacing ? gl_Normal : -gl_Normal);
    vec3 ambient = ambientColor * textureColor.rgb;

    float diff = max(dot(normal, lightDir), 0.0);
    vec3 diffuse = diff * diffuseColor * textureColor.rgb;

    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
    vec3 specular = spec * specularColor;

    float distance = length(cameraPos - fragPos);
    float attenuation = 1.0 / pow(distance, 2);
    
    gl_FlagColor = vec4((ambient + diffuse + specular) * attenuation, textureColor.a);
}