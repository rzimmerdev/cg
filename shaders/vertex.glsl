attribute vec3 position;
attribute vec2 texture_coord;
attribute vec3 normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

varying vec3 out_normal;
varying vec2 out_texture;
varying vec3 out_position;

void main(){
    gl_Position = projection * view * model * vec4(position,1.0);
    out_texture = vec2(texture_coord);
    out_normal = normal;
    out_position = vec3(model * vec4(position,1.0));
}