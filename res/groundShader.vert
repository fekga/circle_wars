#version 330 core

varying vec3 vertex;

uniform float time;

void main()
{
	vertex = gl_Vertex.xyz;
	
	gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}