uniform float time;
varying vec3 N;
varying vec3 v;


void main()
{
    vec4 vertex = vec4(gl_Vertex);
    
    v = vec3(gl_ModelViewMatrix * vertex);       
    N = normalize(gl_NormalMatrix * gl_Normal);
    
    vec4 newPosition = vec4(vertex.x + cos(time*3)*0.25 * N.x, vertex.y + sin(time*5)*0.25 * N.y, vertex.z + cos(time*4)*sin(time*2)*0.3 * N.z, vertex.w) ;
    
    gl_Position = gl_ModelViewProjectionMatrix * newPosition;
}