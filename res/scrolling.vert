uniform float time;
uniform vec2 focus;


void main()
{	
	vec4 vertex = gl_Vertex;
	gl_Position = gl_ModelViewProjectionMatrix * (vertex - vec4(focus,0.0,0.0));
	//gl_Position = gl_ModelViewProjectionMatrix * vertex;
}