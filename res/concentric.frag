uniform float time;
uniform vec2 focus;
uniform vec2 resolution;

float hash( float n ){
    return fract(sin(n)*43758.5453);
}

float noise( vec2 uv ){
    vec3 x = vec3(uv, 0);

    vec3 p = floor(x);
    vec3 f = fract(x);
    
    f       = f*f*(3.0-2.0*f);
    float n = p.x + p.y*57.0 + 113.0*p.z;
    
    return mix(mix(mix( hash(n+0.0), hash(n+1.0),f.x),
                   mix( hash(n+57.0), hash(n+58.0),f.x),f.y),
               mix(mix( hash(n+113.0), hash(n+114.0),f.x),
                   mix( hash(n+170.0), hash(n+171.0),f.x),f.y),f.z);
}

mat2 m = mat2(0.8,0.6,-0.6,0.8);

float fbm(vec2 p)
{
    float f = 0.0;
    f += 0.5000*noise( p ); p*=m*2.02;
    f += 0.2500*noise( p ); p*=m*2.03;
    f += 0.1250*noise( p ); p*=m*2.01;
    f += 0.0625*noise( p );
    f /= 0.9375;
    return f;
}

vec2 transform(vec2 p)
{
 	p = -1.0+2.0*(p/resolution.xy);
    p.x *= resolution.x/resolution.y;
    return p;
}

const float spikes = 8.0;

vec3 getColor()
{
    vec2 p = transform(gl_FragCoord.xy);
    vec2 c = transform(resolution*0.5-focus);
    
    vec3 col =vec3(0.33);
    
    float dist = distance(p,c) * 0.75;
    if(dist > 0.25)
    {
        float angle = atan(c.y-p.y,c.x-p.x);
        float a = cos(spikes*angle)*0.85;
        dist += smoothstep(-1.0,1.0,a)*0.15;
    
        float r = smoothstep(0.0,0.05,sin(dist*15.0));
    
        col = mix(vec3(0.33),vec3(0.66),r);
    }
    
    return col;
}

void main(void)
{   
    vec3 col = getColor();

	gl_FragColor = vec4(col,1.0);
}