uniform float time;
uniform vec2 focus;

void main(){
	
	vec2 p = gl_FragCoord.xy - focus;

	float d = distance(p,focus);

	if(d < 5){
		gl_FragColor = vec4(1.0,0.0,0.0,1.0);
	}else{
		gl_FragColor = vec4(0.0,1.0,0.0,1.0);
	}

}